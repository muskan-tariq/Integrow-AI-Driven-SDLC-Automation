"""
Requirements API router for Phase 1
Handles requirement analysis, chat, export, and approval endpoints
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from dependencies import get_current_user
from models.requirement import (
    AnalysisRequest, AnalysisResponse, Requirement, RequirementCreate, 
    RequirementUpdate, RequirementSummary, ExportRequest, ExportResponse,
    ApprovalRequest, ApprovalResponse, ConversationState, ChatMessage,
    UserStory, ParsedEntities, AmbiguityAnalysis, CompletenessAnalysis, 
    EthicsAnalysis, APIUsageLog
)
from models.project import Project
from services.supabase_service import SupabaseService
from services.llm_service import LLMService
from services.websocket_service import websocket_service
from workflows.analysis_workflow import AnalysisWorkflow
from agents.requirements import OrchestratorAgent
from agents.integration import GitAgent

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/requirements", tags=["requirements"])

# Initialize services
supabase_service = SupabaseService()
llm_service = LLMService()
workflow = AnalysisWorkflow()
orchestrator = OrchestratorAgent()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_requirement(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze a requirement using the multi-agent system
    """
    try:
        start_time = time.time()
        
        # Create requirement record
        requirement_data = {
            "project_id": str(request.project_id),
            "raw_text": request.text,
            "status": "analyzing",
            "created_by": current_user.id
        }
        
        # Insert requirement into database
        result = supabase_service.client.table("requirements").insert(requirement_data).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create requirement record"
            )
        
        requirement_id = result.data[0]["id"]
        session_id = str(uuid.uuid4())
        
        # Run analysis workflow
        logger.info(f"Starting analysis for requirement {requirement_id}")
        
        # Use orchestrator to run the full workflow
        orchestrator_result = await orchestrator.analyze(
            project_id=str(request.project_id),
            text=request.text
        )
        
        # Extract results from orchestrator
        ambiguity_data = orchestrator_result.analysis.get("ambiguity", {})
        completeness_data = orchestrator_result.analysis.get("completeness", {})
        ethics_data = orchestrator_result.analysis.get("ethics", {})
        overall_quality = orchestrator_result.analysis.get("overall_quality_score", 0.0)
        
        # Transform to frontend-expected format
        ambiguity_issues = [
            {
                "id": f"amb_{idx}",
                "type": "ambiguity",
                "severity": "medium",
                "message": issue.get("explanation", ""),
                "location": issue.get("term", ""),
                "suggestions": issue.get("suggestions", []),
            }
            for idx, issue in enumerate(ambiguity_data.get("issues", []))
        ]
        
        completeness_issues = [
            {
                "id": f"comp_{idx}",
                "type": "completeness",
                "severity": issue.get("severity", "medium"),
                "message": issue.get("description", ""),
                "location": issue.get("category", ""),
                "suggestions": [issue.get("suggestion", "")],
            }
            for idx, issue in enumerate(completeness_data.get("missing", []))
        ]
        
        ethics_issues = [
            {
                "id": f"eth_{idx}",
                "type": "ethics",
                "severity": issue.get("severity", "medium"),
                "message": issue.get("description", ""),
                "location": issue.get("category", ""),
                "suggestions": [],
            }
            for idx, issue in enumerate(ethics_data.get("issues", []))
        ]
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Extract user stories from orchestrator result
        user_stories_list = orchestrator_result.user_stories.get("stories", [])
        
        # Prepare response in frontend-expected format
        response_data = {
            "requirement_id": requirement_id,
            "session_id": session_id,
            "quality_score": int(overall_quality * 100),  # Convert 0-1 to 0-100
            "total_issues": len(ambiguity_issues) + len(completeness_issues) + len(ethics_issues),
            "ambiguity_issues": ambiguity_issues,
            "completeness_issues": completeness_issues,
            "ethics_issues": ethics_issues,
            "parsed_entities": {
                "actors": orchestrator_result.parsed.get("actors", []),
                "actions": orchestrator_result.parsed.get("actions", []),
                "entities": orchestrator_result.parsed.get("entities", []),
            },
            "parsed": orchestrator_result.parsed,
            "analysis": {
                "ambiguity": ambiguity_data,
                "completeness": completeness_data,
                "ethics": ethics_data
            },
            "overall_quality_score": overall_quality,
            "api_used": orchestrator_result.analysis.get("api_used", {}),
            "processing_time": processing_time,
            "user_stories": user_stories_list  # Add user stories to response
        }
        
        logger.info(f"Analysis completed for requirement {requirement_id} in {processing_time:.2f}s")
        
        return AnalysisResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Error analyzing requirement: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{requirement_id}", response_model=Requirement)
async def get_requirement(
    requirement_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific requirement by ID
    """
    try:
        # Get requirement from database
        result = supabase_service.client.table("requirements").select("*").eq("id", requirement_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        requirement_data = result.data[0]
        
        # Convert to Pydantic model
        return Requirement(**requirement_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting requirement {requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirement"
        )


@router.get("/project/{project_id}", response_model=List[RequirementSummary])
async def get_project_requirements(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all requirements for a project
    """
    try:
        # Get requirements from database
        result = supabase_service.client.table("requirements").select(
            "id, project_id, version, raw_text, overall_quality_score, status, created_at, updated_at"
        ).eq("project_id", project_id).order("created_at", desc=True).execute()
        
        requirements = []
        for req_data in result.data:
            # Truncate text for summary
            truncated_text = req_data["raw_text"][:200] + "..." if len(req_data["raw_text"]) > 200 else req_data["raw_text"]
            req_data["raw_text"] = truncated_text
            requirements.append(RequirementSummary(**req_data))
        
        return requirements
        
    except Exception as e:
        logger.error(f"Error getting requirements for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirements"
        )


@router.put("/{requirement_id}", response_model=Requirement)
async def update_requirement(
    requirement_id: str,
    update_data: RequirementUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a requirement
    """
    try:
        # Prepare update data
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow().isoformat()
        
        # Update requirement in database
        result = supabase_service.client.table("requirements").update(update_dict).eq("id", requirement_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        return Requirement(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating requirement {requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update requirement"
        )



@router.delete("/{requirement_id}")
async def delete_requirement(
    requirement_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a requirement from database and Git repository
    """
    try:
        # Get requirement to find project and check permissions
        result = supabase_service.client.table("requirements").select("*").eq("id", requirement_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
            
        requirement = result.data[0]
        
        # Get project to find repository path
        project_result = supabase_service.client.table("projects").select("*").eq("id", requirement["project_id"]).execute()
        
        if not project_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
            
        project = project_result.data[0]
        
        # 1. Delete from Supabase
        # Delete related user stories first
        supabase_service.delete_user_stories_by_requirement(requirement_id)
        
        # Delete requirement
        supabase_service.client.table("requirements").delete().eq("id", requirement_id).execute()
        
        # 2. Delete from Git Repository
        try:
            repo_path = Path(project["local_path"])
            if repo_path.exists():
                git_agent = GitAgent(str(repo_path))
                
                # Delete User Stories file
                user_stories_path = f".integrow/user-stories/REQ-{requirement_id}.md"
                await git_agent.delete_file(
                    file_path=user_stories_path,
                    commit_message=f"Delete user stories for REQ-{requirement_id}",
                    branch="main" 
                )
                
                # Delete requirement versions
                history = await git_agent.get_requirement_history(requirement_id)
                deleted_versions = set()
                
                for entry in history:
                    file_path = entry.get("file_path")
                    if file_path and file_path not in deleted_versions:
                        await git_agent.delete_file(
                            file_path=file_path,
                            commit_message=f"Delete requirement REQ-{requirement_id}",
                            branch="main"
                        )
                        deleted_versions.add(file_path)
                
                # Push changes
                await git_agent.push_to_remote()
                
        except Exception as git_error:
            logger.error(f"Error deleting from Git: {git_error}")
            
        return {"message": "Requirement deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting requirement {requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete requirement: {str(e)}"
        )


@router.post("/export", response_model=ExportResponse)
async def export_requirement(
    request: ExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Export a requirement in various formats
    """
    try:
        # Get requirement data
        result = supabase_service.client.table("requirements").select("*").eq("id", str(request.requirement_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        requirement = Requirement(**result.data[0])
        
        # Generate export content based on format
        if request.format == "user_stories":
            content = await _generate_user_stories(requirement)
        elif request.format == "acceptance_criteria":
            content = await _generate_acceptance_criteria(requirement)
        elif request.format == "raw":
            content = requirement.raw_text
        elif request.format == "structured":
            content = requirement.json(indent=2)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid export format"
            )
        
        # Convert to requested output format
        if request.output_format == "yaml":
            import yaml
            content = yaml.dump(json.loads(content) if isinstance(content, str) and content.startswith('{') else {"content": content}, default_flow_style=False)
        elif request.output_format == "markdown":
            content = f"# Requirement Export\n\n{content}"
        elif request.output_format == "csv":
            # For CSV, create a simple table format
            content = f"Field,Value\nRaw Text,\"{requirement.raw_text}\"\nQuality Score,{requirement.overall_quality_score or 'N/A'}\nStatus,{requirement.status}"
        
        return ExportResponse(
            format=request.output_format,
            content=content,
            file_size=len(content.encode('utf-8'))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting requirement {request.requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export requirement"
        )


@router.post("/approve", response_model=ApprovalResponse)
async def approve_requirement(
    request: ApprovalRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Approve a requirement and commit to GitHub
    """
    try:
        # Get requirement data
        result = supabase_service.client.table("requirements").select("*").eq("id", str(request.requirement_id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        requirement = Requirement(**result.data[0])
        
        # Get project to find repository path
        project_result = supabase_service.client.table("projects").select("*").eq("id", str(requirement.project_id)).execute()
        
        if not project_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project_data = project_result.data[0]
        
        # Parse GitHub URL to get username and repo name if missing
        if "github_username" not in project_data or "repo_name" not in project_data:
            github_url = project_data.get("github_repo_url", "")
            if github_url:
                try:
                    if github_url.endswith(".git"):
                        github_url = github_url[:-4]
                    parts = github_url.split("/")
                    project_data["github_username"] = parts[-2]
                    project_data["repo_name"] = parts[-1]
                except Exception:
                    logger.warning(f"Failed to parse GitHub URL: {github_url}")
        
        project = Project(**project_data)
        
        # Use local_path from project data
        repo_path = Path(project.local_path)
        
        if not repo_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository not found at {repo_path}"
            )
        
        # Initialize Git Agent
        git_agent = GitAgent(str(repo_path))
        
        # Prepare requirement data for YAML export
        requirement_data = {
            "id": str(requirement.id),
            "project_id": str(requirement.project_id),
            "raw_text": requirement.raw_text,
            "status": "approved",
            "parsed_entities": requirement.parsed_entities.model_dump() if requirement.parsed_entities else None,
            "ambiguity_analysis": requirement.ambiguity_analysis.model_dump() if requirement.ambiguity_analysis else None,
            "completeness_analysis": requirement.completeness_analysis.model_dump() if requirement.completeness_analysis else None,
            "ethics_analysis": requirement.ethics_analysis.model_dump() if requirement.ethics_analysis else None,
            "overall_quality_score": requirement.overall_quality_score,
            "created_at": requirement.created_at.isoformat() if requirement.created_at else None,
            "approved_at": datetime.utcnow().isoformat(),
            "approved_by": current_user.id
        }
        
        # Commit requirement to .integrow/requirements/
        commit_result = await git_agent.commit_requirement(
            requirement_data=requirement_data,
            commit_message=request.commit_message,
            branch=request.branch
        )
        
        # Update requirement status in database
        new_version = commit_result["version"]
        supabase_service.client.table("requirements").update({
            "status": "approved",
            "version": new_version,
            "approved_by": current_user.id,
            "approved_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", str(request.requirement_id)).execute()
        
        # Construct GitHub commit URL
        # Format: https://github.com/{username}/{repo}/commit/{sha}
        commit_url = f"https://github.com/{project.github_username}/{project.repo_name}/commit/{commit_result['commit_sha']}"
        
        logger.info(f"Successfully approved requirement {request.requirement_id} (version {new_version})")
        
        return ApprovalResponse(
            requirement_id=request.requirement_id,
            version=new_version,
            commit_sha=commit_result["commit_sha"],
            commit_url=commit_url,
            file_path=commit_result["file_path"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving requirement {request.requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve requirement: {str(e)}"
        )


@router.get("/{requirement_id}/history")
async def get_requirement_history(
    requirement_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get version history for a requirement
    """
    try:
        # Get all versions of the requirement
        result = supabase_service.client.table("requirements").select(
            "version, status, overall_quality_score, created_by, approved_by, approved_at, created_at"
        ).eq("id", requirement_id).order("version", desc=True).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requirement not found"
            )
        
        return {
            "requirement_id": requirement_id,
            "versions": result.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history for requirement {requirement_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve requirement history"
        )


@router.websocket("/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat with AI for requirement refinement.
    Supports streaming responses from Groq API.
    """
    await websocket_service.handle_chat(websocket, session_id)


# Helper functions

async def _generate_user_stories(requirement: Requirement) -> str:
    """Generate user stories from requirement"""
    # This would use the LLM service to generate user stories
    # For now, return a mock response
    return f"""User Stories for: {requirement.raw_text[:50]}...

1. As a user, I want to login to the system, so that I can access my account.
2. As an admin, I want to manage user accounts, so that I can maintain system security.
"""


async def _generate_acceptance_criteria(requirement: Requirement) -> str:
    """Generate acceptance criteria from requirement"""
    # This would use the LLM service to generate acceptance criteria
    # For now, return a mock response
    return f"""Acceptance Criteria for: {requirement.raw_text[:50]}...

Given a user wants to login
When they enter valid credentials
Then they should be redirected to the dashboard

Given a user enters invalid credentials
When they submit the login form
Then they should see an error message
"""


async def _get_conversation_state(session_id: str) -> ConversationState:
    """Get conversation state from Redis"""
    # This would retrieve from Redis
    # For now, return a new conversation state
    return ConversationState(
        session_id=session_id,
        requirement_id=uuid.uuid4()  # Mock requirement ID
    )


async def _save_conversation_state(conversation_state: ConversationState):
    """Save conversation state to Redis"""
    # This would save to Redis
    # For now, just log
    logger.info(f"Saving conversation state for session {conversation_state.session_id}")


async def _generate_chat_response(conversation_state: ConversationState) -> Dict[str, Any]:
    """Generate AI response for chat"""
    # This would use the LLM service to generate responses
    # For now, return a mock response
    return {
        "content": "I can help you improve this requirement. Here are some suggestions...",
        "suggestions": [
            "Add specific timing requirements",
            "Define error handling scenarios",
            "Specify user roles and permissions"
        ]
    }
