from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pathlib import Path
import asyncio
import os
from datetime import datetime
import logging

from dependencies import get_current_user
from models.user import UserProfile
from models.project import (
    ProjectCreate, ProjectResponse, ProjectListResponse, 
    ProjectCreateResponse, ProjectUpdate, ProjectActivity
)
from services.supabase_service import supabase_service
from agents.integration import GitHubAgent, GitAgent
from services.encryption import decrypt_token
from config import settings
from services.audit_service import audit_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/create", response_model=ProjectCreateResponse)
async def create_project(
    project_create: ProjectCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new project with GitHub integration"""
    try:
        # Get user's GitHub token
        user_data = supabase_service.client.table('users').select('access_token_encrypted').eq('id', current_user.id).execute()
        if not user_data.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        encrypted_token = user_data.data[0]['access_token_encrypted']
        
        # Initialize GitHub agent
        github_agent = GitHubAgent.from_encrypted_token(encrypted_token)
        
        # Create GitHub repository
        repo_data = await github_agent.create_repository(
            name=project_create.name,
            description=project_create.description,
            private=(project_create.visibility == "private")
        )
        
        # Create local project directory
        project_path = Path(settings.PROJECTS_BASE_DIR) / current_user.github_username / project_create.name
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Git agent
        git_agent = GitAgent(str(project_path))
        
        # Initialize Git repository
        await git_agent.init_repository(repo_data["clone_url"])
        
        # Create project structure based on template
        git_agent.create_project_structure(project_create.template)
        
        # Create initial commit
        initial_commit_sha = await git_agent.create_commit(
            "Initial commit by InteGrow Agent\\n\\nProject created with InteGrow AI-SES Suite"
        )
        
        # Create develop branch
        await git_agent.create_branch("develop", checkout=False)
        
        # Push to GitHub
        await git_agent.push_to_remote("main")
        await git_agent.switch_branch("develop")
        await git_agent.push_to_remote("develop")
        await git_agent.switch_branch("main")
        
        # Create develop branch on GitHub
        await github_agent.create_branch(project_create.name, "develop", "main")
        
        # Save project to database
        project_data = {
            "user_id": current_user.id,
            "name": project_create.name,
            "description": project_create.description,
            "local_path": str(project_path),
            "github_repo_url": repo_data["html_url"],
            "github_repo_id": str(repo_data["id"]),
            "default_branch": "main",
            "visibility": project_create.visibility,
            "template": project_create.template,
            "status": "active"
        }
        
        created_project = await supabase_service.create_project(project_data)
        
        if not created_project:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save project to database"
            )
        
        # Log project creation activity
        await supabase_service.log_project_activity({
            "project_id": created_project["id"],
            "activity_type": "project_created",
            "description": f"Project '{project_create.name}' created with template '{project_create.template}'",
            "metadata": {
                "template": project_create.template,
                "visibility": project_create.visibility,
                "github_repo_id": repo_data["id"],
                "initial_commit": initial_commit_sha
            }
        })
        
        return ProjectCreateResponse(
            project_id=created_project["id"],
            name=project_create.name,
            local_path=str(project_path),
            github_url=repo_data["html_url"],
            branches=["main", "develop"],
            created_at=created_project["created_at"]
        )
        
    except ValueError as e:
        # Repository already exists or validation error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("")
async def get_user_projects(
    current_user: UserProfile = Depends(get_current_user),
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    sort: str = Query(default="created_at", regex="^(created_at|updated_at|name)$")
):
    """Get user's projects with pagination"""
    try:
        projects = await supabase_service.get_user_projects(
            current_user.id, 
            limit=limit, 
            offset=offset
        )
        
        # Return with pagination metadata
        return {
            "projects": [ProjectListResponse(**project).dict() for project in projects],
            "total": len(projects),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting user projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get project details"""
    try:
        project = await supabase_service.get_project(project_id, current_user.id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if user owns the project
        if project["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        
        return ProjectResponse(**project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve project"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Update project details"""
    try:
        # Check if project exists and user owns it
        project = await supabase_service.get_project(project_id, current_user.id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        
        # Filter out None values
        update_data = {k: v for k, v in project_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updated_project = await supabase_service.update_project(project_id, update_data)
        
        if not updated_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Log update activity
        await supabase_service.log_project_activity({
            "project_id": project_id,
            "activity_type": "project_updated",
            "description": f"Project '{project['name']}' updated",
            "metadata": {
                "updated_fields": list(update_data.keys()),
                "updated_by": current_user.github_username
            }
        })
        
        return ProjectResponse(**updated_project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    delete_github: bool = Query(default=False, description="Also delete the GitHub repository"),
    delete_local: bool = Query(default=True, description="Delete local folder"),
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Delete project completely.
    
    - Removes from database (hard delete)
    - Optionally deletes local folder
    - Optionally deletes GitHub repository
    """
    try:
        # Check if project exists and user owns it
        project = await supabase_service.get_project(project_id, current_user.id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        deleted_resources = []
        
        logger.info(f"Delete project {project_id}: delete_local={delete_local}")
        logger.info(f"Project local_path: {project.get('local_path')}")
        
        # 1. Delete local folder if requested
        if delete_local and project.get("local_path"):
            import shutil
            local_path = Path(project["local_path"])
            logger.info(f"Attempting to delete local folder: {local_path}")
            
            try:
                if local_path.exists():
                    # Use shutil.rmtree with onerror handler for permission issues
                    def on_rm_error(func, path, exc_info):
                        import stat
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    
                    shutil.rmtree(str(local_path), onerror=on_rm_error)
                    deleted_resources.append("local_folder")
                    logger.info(f"Successfully deleted local folder: {local_path}")
                else:
                    logger.warning(f"Local folder does not exist: {local_path}")
            except Exception as e:
                logger.error(f"Failed to delete local folder: {e}")
        
        # 2. Delete GitHub repository if requested
        if delete_github and project.get("github_repo_url"):
            try:
                # Get user's GitHub token
                token = decrypt_token(current_user.access_token_encrypted)
                
                # Extract owner/repo from URL
                repo_url = project["github_repo_url"]
                # Example: https://github.com/owner/repo -> owner/repo
                parts = repo_url.rstrip("/").split("/")
                owner, repo_name = parts[-2], parts[-1]
                
                logger.info(f"Attempting to delete GitHub repo: {owner}/{repo_name}")
                
                # Delete repository via GitHub API
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        f"https://api.github.com/repos/{owner}/{repo_name}",
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Accept": "application/vnd.github+json",
                        }
                    )
                    if response.status_code == 204:
                        deleted_resources.append("github_repo")
                        logger.info(f"Deleted GitHub repo: {owner}/{repo_name}")
                    elif response.status_code == 403:
                        logger.warning(f"No permission to delete GitHub repo: {owner}/{repo_name}")
                    elif response.status_code == 404:
                        logger.warning(f"GitHub repo not found (already deleted?): {owner}/{repo_name}")
                    else:
                        logger.warning(f"Failed to delete GitHub repo: {response.status_code} - {response.text}")
            except Exception as e:
                logger.warning(f"Could not delete GitHub repo: {e}")
        
        # 3. Delete related data from database
        # First get requirement IDs for this project
        reqs_result = supabase_service.client.table("requirements").select("id").eq("project_id", project_id).execute()
        req_ids = [r["id"] for r in reqs_result.data] if reqs_result.data else []
        
        # Delete user stories for those requirements
        if req_ids:
            for req_id in req_ids:
                supabase_service.client.table("user_stories").delete().eq("requirement_id", req_id).execute()
        
        # Delete other related data
        supabase_service.client.table("uml_diagrams").delete().eq("project_id", project_id).execute()
        supabase_service.client.table("code_generation_sessions").delete().eq("project_id", project_id).execute()
        supabase_service.client.table("requirements").delete().eq("project_id", project_id).execute()
        
        # 4. Delete the project itself
        supabase_service.client.table("projects").delete().eq("id", project_id).execute()
        deleted_resources.append("database")
        
        logger.info(f"Project {project_id} fully deleted. Resources: {deleted_resources}")
        
        # Audit log
        await audit_service.log_event(
            user_id=current_user.id,
            action="delete_project",
            resource_id=project_id,
            details={
                "project_name": project["name"],
                "deleted_resources": deleted_resources
            }
        )
        
        return {
            "message": "Project deleted successfully",
            "deleted_resources": deleted_resources
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.get("/{project_id}/status")
async def get_project_git_status(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """Get Git status for project"""
    try:
        # Check if project exists and user owns it
        project = await supabase_service.get_project(project_id, current_user.id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )
        
        # Get Git status
        git_agent = GitAgent(project["local_path"])
        git_status = await git_agent.get_status()
        
        return {
            "project_id": project_id,
            "project_name": project["name"],
            "local_path": project["local_path"],
            "github_url": project["github_repo_url"],
            "git_status": git_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project Git status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project Git status"
        )

@router.get("/{project_id}/files", tags=["Projects"])
async def list_project_files(
    project_id: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """List all files in the project directory, useful for code review"""
    try:
        project = await supabase_service.get_project(project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        local_path = project["local_path"]
        if not os.path.exists(local_path):
             raise HTTPException(status_code=400, detail="Project local folder not found")

        files = []
        exclude_dirs = {'.git', 'venv', '__pycache__', 'node_modules', '.next', 'dist', 'build'}
        
        relevant_extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.md', '.json', '.jinja2']
        
        for root, dirs, filenames in os.walk(local_path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in filenames:
                rel_path = os.path.relpath(os.path.join(root, f), local_path).replace("\\", "/")
                ext = os.path.splitext(f)[1].lower()
                if ext in relevant_extensions:
                    files.append({
                        "path": rel_path,
                        "name": f,
                        "extension": ext
                    })

        return {"files": sorted(files, key=lambda x: x["path"])}
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))