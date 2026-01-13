"""
User Stories API Router
Handles user story refinement and approval endpoints
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from dependencies import get_current_user
from models.requirement import UserStory
from agents.user_stories import StoryRefinementAgent
from agents.integration import GitAgent
from services.supabase_service import SupabaseService

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/user-stories", tags=["user-stories"])

# Initialize services
supabase_service = SupabaseService()
refinement_agent = StoryRefinementAgent()


# Request/Response Models

class RefineStoryRequest(BaseModel):
    """Request to refine user stories"""
    story_id: str = Field(..., description="ID of the story being refined request (or batch ID)")
    stories: List[Dict[str, Any]] = Field(..., description="List of stories to refine")
    refinement_request: str = Field(..., min_length=1, description="What to change")
    conversation_history: Optional[List[Dict[str, str]]] = Field(default=None, description="Previous messages")


class RefineStoryResponse(BaseModel):
    """Response from story refinement"""
    refined_stories: List[UserStory] = Field(..., description="Updated stories")
    changes_made: List[str] = Field(..., description="List of changes applied")
    explanation: str = Field(..., description="AI explanation of changes")


class ApproveStoriesRequest(BaseModel):
    """Request to approve and push stories to GitHub"""
    requirement_id: UUID = Field(..., description="ID of the requirement")
    user_stories: List[UserStory] = Field(..., description="Stories to approve")
    commit_message: str = Field(..., min_length=1, max_length=200, description="Git commit message")
    branch: str = Field(default="main", description="Target branch")


class ApproveStoriesResponse(BaseModel):
    """Response from story approval"""
    commit_sha: str = Field(..., description="Git commit SHA")
    commit_url: str = Field(..., description="GitHub commit URL")
    file_path: str = Field(..., description="Path to committed file")
    stories_count: int = Field(..., description="Number of stories committed")


# Endpoints

class UserStoryWithContext(BaseModel):
    """User story with requirement context"""
    id: str
    requirement_id: str
    title: str
    story: str
    acceptance_criteria: List[str]
    priority: str
    story_points: Optional[int] = None
    tags: List[str] = []
    created_at: Optional[str] = None


@router.get("/project/{project_id}", response_model=List[UserStoryWithContext])
async def get_project_user_stories(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all user stories for a project (aggregated from all requirements).
    """
    try:
        logger.info(f"Fetching all user stories for project {project_id}")
        
        # First get all requirements for the project
        reqs_result = supabase_service.client.table("requirements").select(
            "id"
        ).eq("project_id", project_id).execute()
        
        if not reqs_result.data:
            return []
        
        all_stories = []
        for req in reqs_result.data:
            stories_data = supabase_service.get_user_stories_by_requirement(
                req["id"], str(current_user.id)
            )
            for s in stories_data:
                all_stories.append(UserStoryWithContext(
                    id=s.get("id", ""),
                    requirement_id=req["id"],
                    title=s.get("title", ""),
                    story=s.get("story", ""),
                    acceptance_criteria=s.get("acceptance_criteria", []),
                    priority=s.get("priority", "medium"),
                    story_points=s.get("story_points"),
                    tags=s.get("tags", []),
                    created_at=s.get("created_at")
                ))
        
        logger.info(f"Found {len(all_stories)} total user stories for project {project_id}")
        return all_stories
        
    except Exception as e:
        logger.error(f"Error fetching project user stories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user stories: {str(e)}"
        )


@router.get("/requirement/{requirement_id}", response_model=List[UserStory])
async def get_user_stories(
    requirement_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all user stories for a requirement.
    
    Returns stories from database or falls back to GitHub .integrow/ folder.
    """
    try:
        logger.info(f"Fetching user stories for requirement {requirement_id}")
        
        stories_data = supabase_service.get_user_stories_by_requirement(
            requirement_id, str(current_user.id)
        )
        
        if not stories_data:
            return []
        
        # Convert to UserStory models
        stories = []
        for s in stories_data:
            stories.append(UserStory(
                title=s.get("title", ""),
                story=s.get("story", ""),
                acceptance_criteria=s.get("acceptance_criteria", []),
                priority=s.get("priority", "medium"),
                story_points=s.get("story_points"),
                tags=s.get("tags", [])
            ))
        
        logger.info(f"Found {len(stories)} user stories for requirement {requirement_id}")
        return stories
        
    except Exception as e:
        logger.error(f"Error fetching user stories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user stories: {str(e)}"
        )


@router.post("/refine", response_model=RefineStoryResponse)
async def refine_story(
    request: RefineStoryRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Refine a user story using AI based on user feedback.
    
    This endpoint uses Groq API to intelligently refine user stories
    based on user's refinement requests. It maintains conversation context
    for iterative refinement.
    """
    try:
        logger.info(f"Refining story {request.story_id} for user {current_user.id}")
        
        # Call refinement agent
        result = await refinement_agent.refine_stories(
            current_stories=request.stories,
            refinement_request=request.refinement_request,
            conversation_history=request.conversation_history
        )
        
        logger.info(f"Story refinement completed: {len(result.changes_made)} changes made")
        
        return RefineStoryResponse(
            refined_stories=[
                UserStory(
                    title=s.title,
                    story=s.story,
                    acceptance_criteria=s.acceptance_criteria,
                    priority=s.priority,
                    story_points=s.story_points,
                    tags=s.tags
                ) for s in result.refined_stories
            ],
            changes_made=result.changes_made,
            explanation=result.explanation
        )
        
    except Exception as e:
        logger.error(f"Error refining story: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story refinement failed: {str(e)}"
        )


@router.post("/approve", response_model=ApproveStoriesResponse)
async def approve_stories(
    request: ApproveStoriesRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Approve user stories and commit them to GitHub.
    
    This endpoint formats the approved user stories as Markdown and
    commits them to the project's GitHub repository in the
    .integrow/user-stories/ directory.
    """
    try:
        logger.info(f"Approving {len(request.user_stories)} stories for requirement {request.requirement_id}")
        
        # Get requirement data to find project
        requirement_result = supabase_service.client.table("requirements").select(
            "id, project_id, raw_text, created_at"
        ).eq("id", str(request.requirement_id)).execute()
        
        if not requirement_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        requirement_data = requirement_result.data[0]
        
        # Get project data to find repository
        project_result = supabase_service.client.table("projects").select(
            "id, name, github_repo_url, local_path"
        ).eq("id", requirement_data["project_id"]).execute()
        
        if not project_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project_data = project_result.data[0]
        
        # Parse GitHub URL to get username and repo name
        # Expected format: https://github.com/username/repo
        github_url = project_data.get("github_repo_url", "")
        if not github_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project does not have a GitHub repository URL"
            )
            
        try:
            # Remove .git extension if present
            if github_url.endswith(".git"):
                github_url = github_url[:-4]
                
            parts = github_url.split("/")
            github_username = parts[-2]
            repo_name = parts[-1]
        except IndexError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid GitHub URL format: {github_url}"
            )
        
        # Format stories as Markdown
        markdown_content = _format_stories_as_markdown(
            user_stories=request.user_stories,
            requirement_id=str(request.requirement_id),
            requirement_text=requirement_data.get("raw_text", ""),
            created_at=requirement_data.get("created_at")
        )
        
        # Use local_path from project data
        repo_path = Path(project_data["local_path"])
        
        if not repo_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository not found at {repo_path}"
            )
        
        # Initialize Git Agent
        git_agent = GitAgent(str(repo_path))
        
        # Commit stories to GitHub
        file_path = f".integrow/user-stories/REQ-{request.requirement_id}.md"
        
        commit_result = await git_agent.commit_file(
            file_path=file_path,
            content=markdown_content,
            commit_message=request.commit_message,
            branch=request.branch
        )
        
        # Push changes to remote
        await git_agent.push_to_remote(request.branch)
        
        # Construct GitHub commit URL
        commit_url = f"{github_url}/commit/{commit_result['sha']}"
        
        logger.info(f"Successfully committed {len(request.user_stories)} stories to GitHub")
        
        # Save user stories to database as well
        for story in request.user_stories:
            story_data = {
                "requirement_id": str(request.requirement_id),
                "title": story.title,
                "story": story.story,
                "acceptance_criteria": story.acceptance_criteria,
                "priority": story.priority,
                "status": "backlog",
                "story_points": story.story_points,
                "tags": story.tags or [],
            }
            
            # Check if story already exists (by title for simplicity)
            existing = supabase_service.client.table("user_stories").select("id").eq(
                "requirement_id", str(request.requirement_id)
            ).eq("title", story.title).execute()
            
            if existing.data:
                # Update existing story
                supabase_service.client.table("user_stories").update(story_data).eq(
                    "id", existing.data[0]["id"]
                ).execute()
            else:
                # Insert new story
                supabase_service.client.table("user_stories").insert(story_data).execute()
        
        logger.info(f"Saved {len(request.user_stories)} user stories to database")
        
        # Update requirement status to approved
        supabase_service.client.table("requirements").update({
            "status": "approved",
            "approved_by": current_user.id,
            "approved_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", str(request.requirement_id)).execute()
        
        return ApproveStoriesResponse(
            commit_sha=commit_result["sha"],
            commit_url=commit_url,
            file_path=file_path,
            stories_count=len(request.user_stories)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving stories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story approval failed: {str(e)}"
        )


# Helper Functions

def _format_stories_as_markdown(
    user_stories: List[UserStory],
    requirement_id: str,
    requirement_text: str,
    created_at: Optional[str] = None
) -> str:
    """Format user stories as Markdown for GitHub."""
    
    # Header
    timestamp = created_at or datetime.utcnow().isoformat()
    markdown = f"""# User Stories

**Requirement ID**: {requirement_id}  
**Generated**: {timestamp}  
**Status**: Approved  
**Total Stories**: {len(user_stories)}

## Original Requirement

{requirement_text}

---

"""
    
    # Add each story
    for idx, story in enumerate(user_stories, 1):
        markdown += f"""## Story {idx}: {story.title}

**Priority**: {story.priority.capitalize()}  
**Story Points**: {story.story_points or 'Not estimated'}  
**Tags**: {', '.join(story.tags) if story.tags else 'None'}

### User Story

{story.story}

### Acceptance Criteria

"""
        for i, criteria in enumerate(story.acceptance_criteria, 1):
            markdown += f"{i}. {criteria}\n"
        
        markdown += "\n---\n\n"
    
    # Footer
    markdown += f"""
## Metadata

- **Total Priority Breakdown**:
  - High: {sum(1 for s in user_stories if s.priority == 'high')}
  - Medium: {sum(1 for s in user_stories if s.priority == 'medium')}
  - Low: {sum(1 for s in user_stories if s.priority == 'low')}
- **Total Story Points**: {sum(s.story_points or 0 for s in user_stories)}
- **Generated by**: Integrow AI Analysis System
"""
    
    return markdown
