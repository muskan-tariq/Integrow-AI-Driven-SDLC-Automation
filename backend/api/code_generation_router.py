"""
Code Generation API Router

Endpoints for triggering code generation and retrieving results.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from dependencies import get_current_user
from models.user import UserProfile
from models.generated_code import (
    CodeGenerationRequest,
    CodeGenerationResult,
    GeneratedFile,
    CodeGenerationSession,
    GenerationStatus,
    ApproveCodeRequest,
    ApproveCodeResponse,
    ComparisonResult,
    FileDiff,
    ChangeType,
)
from agents.code_generation.orchestrator import CodeGenerationOrchestrator
from services.supabase_service import supabase_service

router = APIRouter(prefix="/api/code-generation", tags=["Code Generation"])
orchestrator = CodeGenerationOrchestrator()


@router.post("/generate", response_model=CodeGenerationResult)
async def generate_code(
    request: CodeGenerationRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Trigger a code generation session.
    """
    try:
        # Verify ownership/access via Supabase project check
        project = await supabase_service.get_project(str(request.project_id), current_user.id)
        if not project or project["user_id"] != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized to access this project")

        # Run generation
        # NOTE: In a production app, this should be a background task (Celery/RQ)
        # For this MVP, we run it await-style (it might take 10-20s)
        result = await orchestrator.generate_code(request)

        # Save session to database
        session_data = {
            "id": str(result.session_id),
            "project_id": str(request.project_id),
            "requirement_id": str(request.requirement_id),
            "uml_diagram_id": str(request.uml_diagram_id) if request.uml_diagram_id else None,
            "user_id": current_user.id,
            "status": result.status.value,
            "tech_stack": request.tech_stack.dict(),
            "generation_scope": request.generation_scope,
            "total_files": result.total_files,
            "total_lines": result.total_lines,
            "generation_time": result.generation_time,
            "api_used": result.api_used
        }
        
        supabase_service.client.table("code_generation_sessions").insert(session_data).execute()

        # Save files to database
        if result.files:
            files_data = [
                {
                    "session_id": str(result.session_id),
                    "file_path": f.file_path,
                    "content": f.content,
                    "file_type": f.file_type.value,
                    "language": f.language,
                    "dependencies": f.dependencies,
                    "description": f.description
                }
                for f in result.files
            ]
            supabase_service.client.table("generated_files").insert(files_data).execute()

        return result

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete a code generation session."""
    try:
        # Verify ownership
        session_res = supabase_service.client.table("code_generation_sessions") \
            .select("project_id, projects(user_id)") \
            .eq("id", str(session_id)) \
            .execute()
            
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
            
        if session_res.data[0]["projects"]["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Delete session (files cascade if configured, otherwise explicitly delete if needed)
        # Assuming cascade delete is set up in SQL
        supabase_service.client.table("code_generation_sessions").delete().eq("id", str(session_id)).execute()
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=CodeGenerationResult)
async def get_session(
    session_id: UUID,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get a code generation session and its files.
    """
    try:
        # Fetch session
        session_res = supabase_service.client.table("code_generation_sessions").select("*").eq("id", str(session_id)).execute()
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_res.data[0]
        
        # Verify access
        if session["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Fetch files
        files_res = supabase_service.client.table("generated_files").select("*").eq("session_id", str(session_id)).execute()
        files = []
        for f in files_res.data:
            files.append(GeneratedFile(**f))

        return CodeGenerationResult(
            session_id=session["id"],
            requirement_id=session["requirement_id"],
            files=files,
            total_files=session["total_files"],
            total_lines=session["total_lines"],
            generation_time=session["generation_time"],
            status=GenerationStatus(session["status"]),
            api_used=session.get("api_used", {}) or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirement/{requirement_id}/latest", response_model=Optional[CodeGenerationResult])
async def get_latest_session_for_requirement(
    requirement_id: UUID,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get the latest code generation session for a requirement.
    """
    try:
        # Fetch latest session
        session_res = supabase_service.client.table("code_generation_sessions") \
            .select("*") \
            .eq("requirement_id", str(requirement_id)) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
            
        if not session_res.data:
            return None
        
        session = session_res.data[0]
        
        # Verify access
        if session["user_id"] != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized")

        # Fetch files
        files_res = supabase_service.client.table("generated_files").select("*").eq("session_id", session["id"]).execute()
        files = [GeneratedFile(**f) for f in files_res.data]

        return CodeGenerationResult(
            session_id=session["id"],
            requirement_id=session["requirement_id"],
            files=files,
            total_files=session["total_files"],
            total_lines=session["total_lines"],
            generation_time=session["generation_time"],
            status=GenerationStatus(session["status"]),
            api_used=session.get("api_used", {}) or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}", response_model=List[CodeGenerationSession])
async def get_project_sessions(
    project_id: UUID,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get all code generation sessions for a project.
    """
    try:
        # Verify project access
        project = await supabase_service.get_project(str(project_id), current_user.id)
        if not project or project.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")

        # Fetch all sessions for this project
        sessions_res = supabase_service.client.table("code_generation_sessions") \
            .select("*") \
            .eq("project_id", str(project_id)) \
            .order("created_at", desc=True) \
            .execute()

        sessions = []
        for s in sessions_res.data:
            sessions.append(CodeGenerationSession(
                id=s["id"],
                project_id=s["project_id"],
                requirement_id=s["requirement_id"],
                user_id=s["user_id"],
                status=GenerationStatus(s["status"]),
                tech_stack=s.get("tech_stack", {}),
                generation_scope=s.get("generation_scope", "full"),
                total_files=s.get("total_files", 0),
                total_lines=s.get("total_lines", 0),
                generation_time=s.get("generation_time", 0.0),
                created_at=s.get("created_at")
            ))

        return sessions

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error fetching project sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve", response_model=ApproveCodeResponse)
async def approve_code_generation(
    request: ApproveCodeRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Approve generated code and commit to repository.
    
    1. Fetch session and files from DB
    2. Write files to local repo
    3. Commit changes
    4. Push to remote
    5. Update session with commit info
    """
    import logging
    from pathlib import Path
    from datetime import datetime
    from agents.integration.git_agent import GitAgent
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Fetch session
        session_res = supabase_service.client.table("code_generation_sessions") \
            .select("*") \
            .eq("id", str(request.session_id)) \
            .execute()
            
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_res.data[0]
        
        # Verify access
        if session["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if already approved
        if session.get("approved_at"):
            raise HTTPException(status_code=400, detail="Session already approved")
        
        # 2. Get project for repo path
        project = await supabase_service.get_project(session["project_id"], current_user.id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        repo_path = project.get("local_path")
        if not repo_path or not Path(repo_path).exists():
            raise HTTPException(
                status_code=400, 
                detail="Project local repository not found. Please clone the repository first."
            )
        
        github_url = project.get("github_repo_url", "")
        
        # 3. Fetch generated files
        files_res = supabase_service.client.table("generated_files") \
            .select("*") \
            .eq("session_id", str(request.session_id)) \
            .execute()
        
        if not files_res.data:
            raise HTTPException(status_code=400, detail="No files to commit")
        
        # 4. Prepare files for commit
        files_to_commit = []
        for f in files_res.data:
            # Prepend target directory to path
            file_path = f"{request.target_directory}/{f['file_path']}"
            files_to_commit.append({
                "path": file_path,
                "content": f["content"]
            })
        
        # 5. Initialize GitAgent and commit
        git_agent = GitAgent(repo_path)
        
        commit_result = await git_agent.commit_multiple_files(
            files=files_to_commit,
            commit_message=request.commit_message,
            branch=request.branch
        )
        
        if not commit_result.get("sha"):
            raise HTTPException(status_code=500, detail="Commit failed - no SHA returned")
        
        # 6. Push to remote
        await git_agent.push_to_remote(request.branch)
        
        # 7. Build commit URL
        clean_url = github_url[:-4] if github_url.endswith(".git") else github_url
        commit_url = f"{clean_url}/commit/{commit_result['sha']}" if clean_url else ""
        
        # 8. Update session in database
        supabase_service.client.table("code_generation_sessions") \
            .update({
                "status": "committed",
                "approved_at": datetime.utcnow().isoformat(),
                "approved_by": current_user.id,
                "commit_sha": commit_result["sha"],
                "commit_url": commit_url
            }) \
            .eq("id", str(request.session_id)) \
            .execute()
        
        logger.info(f"Code approved and committed: {commit_result['sha']}")
        
        return ApproveCodeResponse(
            commit_sha=commit_result["sha"],
            commit_url=commit_url,
            files_committed=commit_result["files_committed"],
            branch=request.branch
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving code: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve code: {str(e)}"
        )


import difflib

@router.get("/sessions/{session_id}/compare", response_model=ComparisonResult)
async def compare_session(
    session_id: UUID,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Compare generated files in a session against the current local codebase.
    """
    from pathlib import Path
    
    try:
        # 1. Fetch Session
        session_res = supabase_service.client.table("code_generation_sessions").select("*").eq("id", str(session_id)).execute()
        if not session_res.data:
            raise HTTPException(status_code=404, detail="Session not found")
        session = session_res.data[0]
        
        if session["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # 2. Get Project Root
        project = await supabase_service.get_project(session["project_id"], current_user.id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        repo_path = Path(project.get("local_path"))
        if not repo_path.exists():
            raise HTTPException(status_code=400, detail="Local repository not found")

        # 3. Fetch Generated Files
        files_res = supabase_service.client.table("generated_files").select("*").eq("session_id", str(session_id)).execute()
        generated_files = [GeneratedFile(**f) for f in files_res.data]

        # 4. Perform Comparison
        diffs = []
        total_changes = 0
        
        for gen_file in generated_files:
            # Assume local path is based on repo root
            local_file_path = repo_path / gen_file.file_path
            
            file_diff = FileDiff(
                file_path=gen_file.file_path,
                change_type=ChangeType.IDENTICAL
            )
            
            if not local_file_path.exists():
                file_diff.change_type = ChangeType.CREATE
                file_diff.new_content = gen_file.content
                file_diff.diff_stat = f"+{len(gen_file.content.splitlines())} -0"
                total_changes += 1
            else:
                try:
                    with open(local_file_path, "r", encoding="utf-8") as f:
                        local_content = f.read()
                    
                    if local_content != gen_file.content:
                        file_diff.change_type = ChangeType.MODIFY
                        file_diff.old_content = local_content
                        file_diff.new_content = gen_file.content
                        
                        # Calculate naive diff stat
                        diff = list(difflib.unified_diff(
                            local_content.splitlines(), 
                            gen_file.content.splitlines(), 
                            lineterm=""
                        ))
                        added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
                        removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
                        file_diff.diff_stat = f"+{added} -{removed}"
                        total_changes += 1
                except UnicodeDecodeError:
                    continue # Skip binary
            
            diffs.append(file_diff)

        return ComparisonResult(
            session_id=session_id,
            project_id=session["project_id"],
            diffs=diffs,
            total_changes=total_changes,
            can_apply_automatically=True
        )

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error comparing session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.post("/sessions/{session_id}/apply", response_model=ApproveCodeResponse)
async def apply_session_changes(
    session_id: UUID, 
    request: ApproveCodeRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Apply (overwrite) the local files with generated code and commit.
    """
    if str(session_id) != str(request.session_id):
        raise HTTPException(status_code=400, detail="Session ID mismatch")
    
    return await approve_code_generation(request, current_user)

