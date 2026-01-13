from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import os
import logging
from datetime import datetime
from models.debt import DebtAnalysisRequest, DebtSession, DebtIssue, DebtAnalysisResponse
from agents.technical_debt import TechnicalDebtAnalyzer
from services.supabase_service import supabase_service
from api.auth_router import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/debt", tags=["Technical Debt"])
analyzer = TechnicalDebtAnalyzer()


@router.get("/project/{project_id}/files")
async def get_project_files(
    project_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get list of code files in the project for selection."""
    try:
        # Verify project exists and user has access
        project_res = supabase_service.client.table("projects") \
            .select("*") \
            .eq("id", str(project_id)) \
            .eq("user_id", current_user.id) \
            .execute()
        
        if not project_res.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = project_res.data[0]
        local_path = project["local_path"]
        
        if not os.path.exists(local_path):
            raise HTTPException(status_code=400, detail="Project path does not exist")
        
        # Collect code files
        code_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php'}
        exclude_dirs = {'.git', 'venv', '__pycache__', 'node_modules', '.next', 'dist', 'build', 'coverage'}
        
        files = []
        for root, dirs, filenames in os.walk(local_path):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # Limit depth
            depth = root[len(local_path):].count(os.sep)
            if depth >= 10:
                dirs[:] = []
                continue
            
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in code_extensions:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, local_path).replace("\\", "/")
                    
                    # Get file size
                    try:
                        size = os.path.getsize(full_path)
                        files.append({
                            "path": rel_path,
                            "name": filename,
                            "extension": ext,
                            "size": size
                        })
                    except:
                        pass
        
        return {"files": files}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=DebtAnalysisResponse)
async def analyze_project(
    request: DebtAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze a project for technical debt."""
    try:
        # 1. Verify project exists and user has access
        project_res = supabase_service.client.table("projects") \
            .select("*") \
            .eq("id", str(request.project_id)) \
            .eq("user_id", current_user.id) \
            .execute()
        
        if not project_res.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = project_res.data[0]
        local_path = project["local_path"]
        
        if not os.path.exists(local_path):
            raise HTTPException(status_code=400, detail="Project path does not exist")
        
        # 2. Calculate next version
        version_res = supabase_service.client.table("debt_sessions") \
            .select("version") \
            .eq("project_id", str(request.project_id)) \
            .order("version", desc=True) \
            .limit(1) \
            .execute()
        
        next_version = (version_res.data[0]["version"] + 1) if version_res.data else 1
        
        # 3. Create session
        session_data = {
            "project_id": str(request.project_id),
            "version": next_version,
            "status": "in_progress",
            "overall_score": 0,
            "complexity_score": 0,
            "duplication_score": 0,
            "dependency_score": 0,
            "total_issues": 0,
            "critical_issues": 0,
            "estimated_hours": 0,
            "summary": f"Technical debt analysis V{next_version}"
        }
        
        session_res = supabase_service.client.table("debt_sessions").insert(session_data).execute()
        if not session_res.data:
            raise HTTPException(status_code=500, detail="Failed to create debt session")
        
        session_id = session_res.data[0]["id"]
        
        # 4. Run analysis
        logger.info(f"Starting debt analysis for project {request.project_id}")
        analysis_result = await analyzer.analyze_project(
            local_path,
            include_tests=request.include_tests,
            max_depth=request.max_depth,
            specific_files=request.specific_files
        )
        
        # 5. Save issues to database
        saved_issues = []
        for issue in analysis_result["issues"]:
            issue_data = {
                "session_id": session_id,
                "file_path": issue["file_path"],
                "issue_type": issue["issue_type"],
                "category": issue["category"],
                "severity": issue["severity"],
                "title": issue["title"],
                "description": issue["description"],
                "line_start": issue.get("line_start"),
                "line_end": issue.get("line_end"),
                "code_snippet": issue.get("code_snippet"),
                "suggested_fix": issue.get("suggested_fix"),
                "estimated_hours": issue.get("estimated_hours", 0)
            }
            
            res = supabase_service.client.table("debt_issues").insert(issue_data).execute()
            if res.data:
                saved_issues.append(res.data[0])
        
        # 6. Update session with final results
        files_text = f"{len(request.specific_files)} specific files" if request.specific_files else f"{analysis_result['files_analyzed']} files"
        
        update_data = {
            "overall_score": analysis_result["overall_score"],
            "complexity_score": analysis_result["complexity_score"],
            "duplication_score": analysis_result["duplication_score"],
            "dependency_score": analysis_result["dependency_score"],
            "total_issues": analysis_result["total_issues"],
            "critical_issues": analysis_result["critical_issues"],
            "estimated_hours": analysis_result["estimated_hours"],
            "status": "completed",
            "summary": f"Analyzed {files_text}, found {analysis_result['total_issues']} issues"
        }
        
        supabase_service.client.table("debt_sessions").update(update_data).eq("id", session_id).execute()
        
        return DebtAnalysisResponse(
            status="success",
            session_id=session_id,
            version=next_version,
            overall_score=analysis_result["overall_score"],
            total_issues=analysis_result["total_issues"],
            critical_issues=analysis_result["critical_issues"],
            estimated_hours=analysis_result["estimated_hours"],
            issues=[DebtIssue(**issue) for issue in analysis_result["issues"]]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in debt analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}")
async def get_project_sessions(
    project_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get all debt analysis sessions for a project."""
    res = supabase_service.client.table("debt_sessions") \
        .select("*, debt_issues(count)") \
        .eq("project_id", str(project_id)) \
        .order("created_at", desc=True) \
        .execute()
    
    return res.data


@router.get("/session/{session_id}")
async def get_session_details(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed issues for a specific debt session."""
    res = supabase_service.client.table("debt_sessions") \
        .select("*, debt_issues(*)") \
        .eq("id", str(session_id)) \
        .execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return res.data[0]


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete a debt analysis session and all its issues."""
    try:
        # Verify ownership
        session_res = supabase_service.client.table("debt_sessions") \
            .select("*, projects(*)") \
            .eq("id", str(session_id)) \
            .execute()
        
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_res.data[0]
        project = session["projects"]

        if project["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Delete from GitHub if exported
        if session.get("github_exported"):
            try:
                # Reconstruct filename
                timestamp = session["created_at"].split(".")[0].replace(":", "-").replace("T", "_")
                filename = f"technical_debt_v{session['version']}_{timestamp}.md"
                report_path = f".integrow/debt/{filename}"

                # Get GitHub Agent
                user_res = supabase_service.client.table("users").select("access_token_encrypted").eq("id", current_user.id).execute()
                if user_res.data and project.get("github_repo_url"):
                     encrypted_token = user_res.data[0]["access_token_encrypted"]
                     from agents.integration.github_agent import GitHubAgent
                     github_agent = GitHubAgent.from_encrypted_token(encrypted_token)
                     
                     repo_name = project["github_repo_url"].split("/")[-1]
                     if repo_name.endswith(".git"):
                         repo_name = repo_name[:-4]

                     await github_agent.delete_file(
                         repo_name=repo_name,
                         path=report_path,
                         message=f"docs: delete technical debt analysis V{session['version']}",
                         branch=project.get("default_branch", "main")
                     )
            except Exception as e:
                logger.error(f"Failed to delete file from GitHub: {e}")
                # We continue to delete from DB even if GitHub delete fails

        supabase_service.client.table("debt_sessions").delete().eq("id", str(session_id)).execute()
        return {"status": "success", "message": "Debt session deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/export-github")
async def export_session_to_github(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Export technical debt report to GitHub."""
    try:
        # 1. Fetch session with all issues
        session_res = supabase_service.client.table("debt_sessions") \
            .select("*, projects(*), debt_issues(*)") \
            .eq("id", str(session_id)) \
            .execute()
        
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_res.data[0]
        project = session["projects"]
        issues = session["debt_issues"]
        
        # Verify ownership
        if project["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # 2. Format as Markdown report
        timestamp = session["created_at"].split(".")[0].replace(":", "-").replace("T", "_")
        filename = f"technical_debt_v{session['version']}_{timestamp}.md"
        report_path = f".integrow/debt/{filename}"
        
        md_content = f"""# Technical Debt Analysis - Version {session['version']}
**Date:** {session['created_at']}
**Overall Score:** {session['overall_score']}/100
**Total Issues:** {session['total_issues']} ({session['critical_issues']} critical)
**Estimated Effort:** {session['estimated_hours']:.1f} hours

## Summary
{session.get('summary', 'Technical debt analysis')}

## Scores by Category
- **Complexity:** {session['complexity_score']}/100
- **Duplication:** {session['duplication_score']}/100
- **Dependencies:** {session['dependency_score']}/100

---

## Issues Detected ({len(issues)})

"""
        
        # Group issues by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_issues = [i for i in issues if i['severity'] == severity]
            if not severity_issues:
                continue
            
            md_content += f"\n### {severity.upper()} Priority ({len(severity_issues)} issues)\n\n"
            
            for issue in severity_issues:
                md_content += f"""#### {issue['title']}
- **File:** `{issue['file_path']}`
- **Type:** {issue['category']}
- **Lines:** {issue.get('line_start', 'N/A')}
- **Effort:** {issue['estimated_hours']:.1f}h

{issue['description']}

"""
                if issue.get('suggested_fix'):
                    md_content += f"**Suggested Fix:**\n{issue['suggested_fix']}\n\n"
                
                md_content += "---\n\n"
        
        # 3. Push to GitHub
        user_res = supabase_service.client.table("users").select("access_token_encrypted").eq("id", current_user.id).execute()
        encrypted_token = user_res.data[0]["access_token_encrypted"]
        
        from agents.integration.github_agent import GitHubAgent
        github_agent = GitHubAgent.from_encrypted_token(encrypted_token)
        
        repo_name = project["github_repo_url"].split("/")[-1]
        
        result = await github_agent.create_or_update_file(
            repo_name=repo_name,
            path=report_path,
            content=md_content,
            message=f"docs: add technical debt analysis V{session['version']} ({session['total_issues']} issues)",
            branch=project.get("default_branch", "main")
        )
        
        # 4. Update session with export status
        commit_sha = result["commit"]
        export_time = datetime.utcnow().isoformat()
        
        supabase_service.client.table("debt_sessions").update({
            "github_exported": True,
            "github_commit_sha": commit_sha,
            "github_exported_at": export_time
        }).eq("id", str(session_id)).execute()
        
        return {
            "status": "success",
            "github_path": report_path,
            "commit_sha": commit_sha,
            "issues_exported": len(issues)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting debt session to GitHub: {e}")
        raise HTTPException(status_code=500, detail=str(e))
