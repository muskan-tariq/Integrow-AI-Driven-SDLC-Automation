from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from uuid import UUID
import os
import logging
from models.review import ReviewRequest, CodeReviewReport, ReviewIssue
from agents.code_review.reviewer_agent import CodeReviewerAgent
from services.supabase_service import supabase_service
from api.auth_router import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/review", tags=["Code Review"])
reviewer = CodeReviewerAgent()

@router.post("/analyze")
async def analyze_files(
    request: ReviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger AI code review for one or more files.
    """
    try:
        # 1. Verify project exists and user has access
        # Fix TypeError: current_user is UserProfile, use .id
        project_res = supabase_service.client.table("projects").select("*").eq("id", str(request.project_id)).eq("user_id", current_user.id).execute()
        
        if not project_res.data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = project_res.data[0]
        local_path = project["local_path"]
        
        # 2. Collect all files to review
        files_to_review = []
        exclude_dirs = {'.git', 'venv', '__pycache__', 'node_modules', '.next', 'dist', 'build'}
        relevant_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css'}

        for path in request.file_paths:
            abs_path = os.path.join(local_path, path)
            if not os.path.exists(abs_path):
                continue
                
            if os.path.isdir(abs_path):
                # Scan directory
                for root, dirs, filenames in os.walk(abs_path):
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    for f in filenames:
                        if os.path.splitext(f)[1].lower() in relevant_extensions:
                            rel_file_path = os.path.relpath(os.path.join(root, f), local_path).replace("\\", "/")
                            files_to_review.append(rel_file_path)
            else:
                files_to_review.append(path.replace("\\", "/"))

        if not files_to_review:
            raise HTTPException(status_code=400, detail="No valid files found for review")

        # 3. Create a Review Session for this batch
        version_res = supabase_service.client.table("review_sessions").select("version").eq("project_id", str(request.project_id)).order("version", desc=True).limit(1).execute()
        next_version = (version_res.data[0]["version"] + 1) if version_res.data else 1

        session_data = {
            "project_id": str(request.project_id),
            "version": next_version,
            "status": "in_progress",
            "score": 0,
            "summary": f"Batch review of {len(files_to_review)} files"
        }
        session_res = supabase_service.client.table("review_sessions").insert(session_data).execute()
        if not session_res.data:
            raise HTTPException(status_code=500, detail="Failed to create review session")
        
        session_id = session_res.data[0]["id"]
        all_results = []
        total_score = 0

        # 4. Perform analysis
        for file_path in files_to_review:
            file_abs_path = os.path.join(local_path, file_path)
            try:
                if not os.path.exists(file_abs_path):
                    continue

                with open(file_abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                analysis_result = await reviewer.review_file(file_path, content)
                if not analysis_result:
                    logger.error(f"Analysis failed for {file_path}")
                    continue
                    
                file_score = analysis_result.get("score", 0)
                total_score += file_score
                
                # Save individual code review linked to session
                review_data = {
                    "session_id": session_id,
                    "project_id": str(request.project_id),
                    "file_path": file_path,
                    "status": "completed",
                    "score": file_score,
                    "version": next_version, # Keep file version in sync with session version
                    "summary": analysis_result.get("summary", "")
                }
                
                res = supabase_service.client.table("code_reviews").insert(review_data).execute()
                if res.data:
                    saved_review = res.data[0]
                    issues_to_save = []
                    for issue in analysis_result.get("issues", []):
                        issues_to_save.append({
                            "review_id": saved_review["id"],
                            "line_number": issue.get("line_number"),
                            "issue_type": issue.get("issue_type"),
                            "severity": issue.get("severity"),
                            "description": issue.get("description"),
                            "suggested_fix": issue.get("suggested_fix")
                        })
                    
                    if issues_to_save:
                        supabase_service.client.table("review_issues").insert(issues_to_save).execute()
                    
                    all_results.append({
                        "file_path": file_path,
                        "id": saved_review["id"],
                        "score": file_score,
                        "summary": analysis_result.get("summary", ""),
                        "issues": analysis_result.get("issues", [])
                    })
            except Exception as e:
                logger.error(f"Error reviewing {file_path}: {e}")
                continue

        # 5. Update session with final results
        avg_score = int(total_score / len(all_results)) if all_results else 0
        supabase_service.client.table("review_sessions").update({
            "score": avg_score,
            "status": "completed"
        }).eq("id", session_id).execute()

        return {
            "status": "success",
            "session_id": session_id,
            "version": next_version,
            "score": avg_score,
            "files_reviewed": len(all_results),
            "results": all_results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in review process: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project/{project_id}")
async def get_project_sessions(
    project_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get all review sessions for a project with their aggregated results."""
    # Fetch sessions with their linked reports count
    res = supabase_service.client.table("review_sessions") \
        .select("*, code_reviews(count)") \
        .eq("project_id", str(project_id)) \
        .order("created_at", desc=True) \
        .execute()
    return res.data

@router.get("/session/{session_id}")
async def get_session_details(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed reports and issues for a specific review session."""
    res = supabase_service.client.table("review_sessions") \
        .select("*, code_reviews(*, review_issues(*))") \
        .eq("id", str(session_id)) \
        .execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = res.data[0]
    logger.info(f"Session data: {session_data.keys()}")
    if "code_reviews" in session_data:
        logger.info(f"Number of reports: {len(session_data['code_reviews'])}")
        if len(session_data['code_reviews']) > 0:
            logger.info(f"First report keys: {session_data['code_reviews'][0].keys()}")
            logger.info(f"First report file_path: {session_data['code_reviews'][0].get('file_path')}")
            
    return session_data

@router.post("/{review_id}/export-github")
async def export_review_to_github(
    review_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Export a code review report to GitHub."""
    try:
        # 1. Fetch review and its issues
        review_res = supabase_service.client.table("code_reviews").select("*, projects(*), review_issues(*)").eq("id", str(review_id)).execute()
        
        if not review_res.data:
            raise HTTPException(status_code=404, detail="Review not found")
            
        review = review_res.data[0]
        project = review["projects"]
        issues = review["review_issues"]
        
        # Verify ownership
        if project["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 2. Format as Markdown
        timestamp = review["created_at"].split(".")[0].replace(":", "-").replace("T", "_")
        filename = f"review_{timestamp}.md"
        report_path = f".integrow/reviews/{filename}"
        
        md_content = f"""# AI Code Review Report - {review['file_path']}
**Date:** {review['created_at']}
**Quality Score:** {review['score']}/100

## Summary
{review['summary']}

## Findings ({len(issues)})
"""
        for issue in issues:
            md_content += f"""
### [{issue['severity'].upper()}] {issue['issue_type']} (Line {issue['line_number']})
**Description:** {issue['description']}
"""
            if issue['suggested_fix']:
                md_content += f"**Suggested Fix:**\n```\n{issue['suggested_fix']}\n```\n"

        # 3. Push to GitHub
        user_res = supabase_service.client.table("users").select("access_token_encrypted").eq("id", current_user.id).execute()
        encrypted_token = user_res.data[0]["access_token_encrypted"]
        
        from agents.integration.github_agent import GitHubAgent
        github_agent = GitHubAgent.from_encrypted_token(encrypted_token)
        
        # Get repo name from URL (e.g., https://github.com/user/repo -> repo)
        repo_name = project["github_repo_url"].split("/")[-1]
        
        result = await github_agent.create_or_update_file(
            repo_name=repo_name,
            path=report_path,
            content=md_content,
            message=f"docs: add AI code review report for {review['file_path']}",
            branch=project.get("default_branch", "main")
        )

        # Update review with GitHub export status
        from datetime import datetime
        supabase_service.client.table("code_reviews").update({
            "github_exported": True,
            "github_commit_sha": result["commit"],
            "github_exported_at": datetime.utcnow().isoformat()
        }).eq("id", str(review_id)).execute()

        return {
            "status": "success",
            "github_path": report_path,
            "commit_sha": result["commit"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting review to GitHub: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/export-github")
async def export_session_to_github(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Export an entire review session (batch) to GitHub as a consolidated report."""
    try:
        from datetime import datetime
        
        # 1. Fetch session with all reviews and issues
        session_res = supabase_service.client.table("review_sessions") \
            .select("*, projects(*), code_reviews(*, review_issues(*))") \
            .eq("id", str(session_id)) \
            .execute()
        
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
            
        session = session_res.data[0]
        project = session["projects"]
        reviews = session["code_reviews"]
        
        # Verify ownership
        if project["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 2. Format as consolidated Markdown report
        timestamp = session["created_at"].split(".")[0].replace(":", "-").replace("T", "_")
        filename = f"review_session_v{session['version']}_{timestamp}.md"
        report_path = f".integrow/reviews/{filename}"
        
        md_content = f"""# AI Code Review Session - Version {session['version']}
**Date:** {session['created_at']}
**Overall Quality Score:** {session['score']}/100
**Files Reviewed:** {len(reviews)}

## Session Summary
{session.get('summary', 'Batch code review analysis')}

---

"""
        
        # Add each file's review
        for idx, review in enumerate(reviews, 1):
            issues = review.get("review_issues", [])
            md_content += f"""## {idx}. {review.get('file_path', 'Unknown File')}
**Score:** {review['score']}/100
**Summary:** {review.get('summary', 'No summary available')}

"""
            if issues:
                md_content += f"### Issues Found ({len(issues)})\n\n"
                for issue in issues:
                    md_content += f"""#### [{issue['severity'].upper()}] {issue['issue_type']}
- **Line:** {issue.get('line_number', 'N/A')}
- **Description:** {issue['description']}
"""
                    if issue.get('suggested_fix'):
                        md_content += f"- **Suggested Fix:**\n```\n{issue['suggested_fix']}\n```\n"
                    md_content += "\n"
            else:
                md_content += "âœ… No issues detected in this file.\n\n"
            
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
            message=f"docs: add AI code review session V{session['version']} ({len(reviews)} files)",
            branch=project.get("default_branch", "main")
        )

        # 4. Update session and all reviews with GitHub export status
        commit_sha = result["commit"]
        export_time = datetime.utcnow().isoformat()
        
        supabase_service.client.table("review_sessions").update({
            "github_exported": True,
            "github_commit_sha": commit_sha,
            "github_exported_at": export_time
        }).eq("id", str(session_id)).execute()
        
        # Also mark all individual reviews as exported
        for review in reviews:
            supabase_service.client.table("code_reviews").update({
                "github_exported": True,
                "github_commit_sha": commit_sha,
                "github_exported_at": export_time
            }).eq("id", review["id"]).execute()

        return {
            "status": "success",
            "github_path": report_path,
            "commit_sha": commit_sha,
            "files_exported": len(reviews)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting session to GitHub: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def delete_review_session(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Delete an entire review session and all its reports."""
    try:
        # Verify ownership via project
        session_res = supabase_service.client.table("review_sessions") \
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
                timestamp = session["created_at"].split(".")[0].replace(":", "-").replace("T", "_")
                filename = f"review_session_v{session['version']}_{timestamp}.md"
                report_path = f".integrow/reviews/{filename}"

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
                         message=f"docs: delete review session V{session['version']}",
                         branch=project.get("default_branch", "main")
                     )
            except Exception as e:
                logger.error(f"Failed to delete file from GitHub: {e}")
                # Continue deletion
            
        supabase_service.client.table("review_sessions").delete().eq("id", str(session_id)).execute()
        return {"status": "success", "message": "Review session deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
