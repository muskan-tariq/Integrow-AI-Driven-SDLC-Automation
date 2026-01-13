"""
UML Diagram API Router

Handles UML diagram generation, retrieval, updates, and rendering.
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse

from models.uml_diagram import (
    UMLGenerationRequest,
    UMLGenerationResponse,
    UMLDiagramResponse,
    UMLDiagramUpdate,
    UMLDiagramListResponse,
)
from models.user import UserResponse, UserProfile
from dependencies import get_current_user
from workflows.uml_workflow import UMLWorkflow
from services.supabase_service import SupabaseService
from agents.integration import GitAgent
from models.uml_diagram import ApproveUMLRequest, ApproveUMLResponse
from models.project import Project
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["UML Diagrams"])


@router.post(
    "/projects/{project_id}/requirements/{requirement_id}/uml/generate",
    response_model=UMLGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_class_diagram(
    project_id: UUID,
    requirement_id: UUID,
    request: UMLGenerationRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Generate UML class diagram from user stories.

    Args:
        project_id: UUID of the project
        requirement_id: UUID of the requirement
        request: Generation options (story IDs, regenerate flag)
        current_user: Authenticated user

    Returns:
        UMLGenerationResponse with diagram details and URLs
    """
    supabase = SupabaseService()
    try:
        logger.info(
            f"User {current_user.id} generating UML diagram for requirement {requirement_id}"
        )

        # Verify project ownership
        project = await supabase.get_project(str(project_id), str(current_user.id))
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied",
            )

        # Check for existing diagram if not regenerating
        if not request.regenerate:
            existing = supabase.get_uml_diagram_by_requirement(
                str(requirement_id), str(current_user.id)
            )
            if existing:
                logger.info(f"Returning cached diagram {existing['id']}")
                return _build_generation_response(existing)

        # Fetch user stories
        user_stories = supabase.get_user_stories_by_requirement(
            str(requirement_id), str(current_user.id)
        )

        if not user_stories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user stories found for this requirement. Generate user stories first.",
            )

        # Filter by specific story IDs if provided
        if request.user_story_ids:
            story_ids = [str(sid) for sid in request.user_story_ids]
            user_stories = [s for s in user_stories if s["id"] in story_ids]

        if not user_stories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No matching user stories found",
            )

        # Generate diagram
        workflow = UMLWorkflow()
        result = await workflow.generate_class_diagram(
            user_stories, requirement_id, project_id
        )

        return _save_and_return_response(
            supabase,
            project_id,
            requirement_id,
            current_user.id,
            result,
        )

    except Exception as e:
        logger.error(f"UML generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/projects/{project_id}/uml/sync",
    response_model=UMLGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def sync_uml_from_code(
    project_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Sync UML diagram from existing code (Architecture Discovery).
    Creates a new version of the diagram based on code structure.
    """
    supabase = SupabaseService()
    try:
        logger.info(f"User {current_user.id} syncing UML from code for project {project_id}")

        # Verify project ownership
        project = await supabase.get_project(str(project_id), str(current_user.id))
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied",
            )

        project_path = project.get("local_path")
        if not project_path:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project has no local path defined",
            )

        # Run Sync Workflow
        workflow = UMLWorkflow()
        result = await workflow.sync_from_code(project_path)

        # For sync, we might not have a requirement_id. 
        # But our DB schema requires it.
        # We should find the "latest" requirement or create a "System Architecture" placeholder?
        # For now, let's look for the most recent requirement or any requirement
        # If none, we might need to handle this.
        # Strategically, attaching to the "latest" requirement makes sense for context.
        
        requirements = supabase.get_requirements_by_project(str(project_id))
        if requirements:
            requirement_id = UUID(requirements[0]["id"])
        else:
             # This is an edge case: Code exists but no requirements in DB.
             # Ideally we should create a dummy requirement or make requirement_id optional in DB.
             # Given migrations are risky, let's defer. For now require at least one requirement.
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No requirements found. Please create a requirement first to anchor the diagram.",
            )

        return _save_and_return_response(
            supabase,
            project_id,
            requirement_id,
            current_user.id,
            result,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UML sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/projects/{project_id}/uml",
    response_model=UMLDiagramListResponse,
)
async def get_project_uml_diagrams(
    project_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Get all UML diagrams for a project.
    """
    supabase = SupabaseService()
    try:
        # Verify project ownership
        project = await supabase.get_project(str(project_id), str(current_user.id))
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied",
            )

        # Get all diagrams for this project
        offset = (page - 1) * page_size
        response = supabase.client.table("uml_diagrams").select(
            "*"
        ).eq("project_id", str(project_id)).eq("user_id", str(current_user.id)).order(
            "created_at", desc=True
        ).range(offset, offset + page_size - 1).execute()

        diagrams = [UMLDiagramResponse(**d) for d in response.data]
        total = len(response.data)

        return UMLDiagramListResponse(
            diagrams=diagrams,
            total=total,
            page=page,
            page_size=page_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project UML diagrams: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch UML diagrams",
        )


@router.get(
    "/uml/{diagram_id}",
    response_model=UMLDiagramResponse,
)
async def get_uml_diagram(
    diagram_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Get UML diagram by ID.

    Args:
        diagram_id: UUID of the diagram
        current_user: Authenticated user

    Returns:
        UMLDiagramResponse with diagram details
    """
    supabase = SupabaseService()
    try:
        diagram = supabase.get_uml_diagram(str(diagram_id), str(current_user.id))

        if not diagram:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="UML diagram not found or access denied",
            )

        return UMLDiagramResponse(**diagram)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching UML diagram: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch UML diagram",
        )


@router.get(
    "/uml/{diagram_id}/render",
)
async def render_uml_diagram(
    diagram_id: UUID,
    format: str = Query(default="svg", regex="^(svg|png)$"),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Render UML diagram in specified format.

    Args:
        diagram_id: UUID of the diagram
        format: Output format (svg or png)
        current_user: Authenticated user

    Returns:
        Image file in requested format
    """
    supabase = SupabaseService()
    try:
        diagram = supabase.get_uml_diagram(str(diagram_id), str(current_user.id))

        if not diagram:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="UML diagram not found or access denied",
            )

        # Return cached SVG if available and requested
        if format == "svg" and diagram.get("rendered_svg"):
            return Response(
                content=diagram["rendered_svg"],
                media_type="image/svg+xml",
                headers={
                    "Content-Disposition": f'inline; filename="diagram_{diagram_id}.svg"'
                },
            )

        # Render on-demand
        workflow = UMLWorkflow()
        rendered = await workflow.export_diagram(
            diagram["plantuml_code"], format=format
        )

        media_type = "image/svg+xml" if format == "svg" else "image/png"
        extension = format

        return Response(
            content=rendered,
            media_type=media_type,
            headers={
                "Content-Disposition": f'inline; filename="diagram_{diagram_id}.{extension}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering UML diagram: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to render UML diagram",
        )


@router.put(
    "/uml/{diagram_id}",
    response_model=UMLDiagramResponse,
)
async def update_uml_diagram(
    diagram_id: UUID,
    update_data: UMLDiagramUpdate,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Update UML diagram (e.g., edit PlantUML code).

    Args:
        diagram_id: UUID of the diagram
        update_data: Fields to update
        current_user: Authenticated user

    Returns:
        Updated UMLDiagramResponse
    """
    supabase = SupabaseService()
    try:
        # Verify diagram exists and user has access
        existing = supabase.get_uml_diagram(str(diagram_id), str(current_user.id))

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="UML diagram not found or access denied",
            )

        # If PlantUML code is updated, re-render
        update_dict = update_data.model_dump(exclude_unset=True)

        if "plantuml_code" in update_dict:
            workflow = UMLWorkflow()
            rendered_svg = await workflow.regenerate_diagram(update_dict["plantuml_code"])
            update_dict["rendered_svg"] = rendered_svg.decode("utf-8")

        # Increment version
        if update_dict:
            update_dict["version"] = existing.get("version", 1) + 1

        # Update in database
        updated = supabase.update_uml_diagram(
            str(diagram_id), str(current_user.id), update_dict
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update diagram",
            )

        logger.info(f"UML diagram {diagram_id} updated to version {update_dict.get('version')}")

        return UMLDiagramResponse(**updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating UML diagram: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update UML diagram: {str(e)}",
        )


@router.get(
    "/projects/{project_id}/requirements/{requirement_id}/uml",
    response_model=UMLDiagramListResponse,
)
async def list_uml_diagrams(
    project_id: UUID,
    requirement_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: UserProfile = Depends(get_current_user),
):
    """
    List all UML diagrams for a requirement.

    Args:
        project_id: UUID of the project
        requirement_id: UUID of the requirement
        page: Page number (1-indexed)
        page_size: Items per page
        current_user: Authenticated user

    Returns:
        UMLDiagramListResponse with paginated diagrams
    """
    supabase = SupabaseService()
    try:
        # Verify project ownership
        project = await supabase.get_project(str(project_id), str(current_user.id))
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied",
            )

        # Get diagrams
        diagrams = supabase.list_uml_diagrams(
            str(requirement_id), str(current_user.id), page=page, page_size=page_size
        )

        total = len(diagrams)  # In production, use COUNT query

        return UMLDiagramListResponse(
            diagrams=[UMLDiagramResponse(**d) for d in diagrams],
            total=total,
            page=page,
            page_size=page_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing UML diagrams: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list UML diagrams",
        )


@router.delete(
    "/uml/{diagram_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_uml_diagram(
    diagram_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Delete UML diagram.
    """
    supabase = SupabaseService()
    try:
        # Verify diagram exists
        existing = supabase.get_uml_diagram(str(diagram_id), str(current_user.id))

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="UML diagram not found or access denied",
            )

        # Try to delete from Git (Artifacts)
        try:
            project = await supabase.get_project(existing["project_id"], str(current_user.id))
            if project and "local_path" in project:
                repo_path = Path(project["local_path"])
                if repo_path.exists():
                     git_agent = GitAgent(str(repo_path))
                     
                     # Define paths
                     puml_filename = f"docs/uml/REQ-{existing['requirement_id']}_class_diagram.puml"
                     svg_filename = f"docs/uml/REQ-{existing['requirement_id']}_class_diagram.svg"
                     
                     # Delete .puml
                     await git_agent.delete_file(
                         file_path=puml_filename,
                         commit_message=f"docs: delete UML source for REQ-{existing['requirement_id']}",
                         branch=project.get("default_branch", "main") # Assuming access to default_branch, otherwise default 'main'
                     )
                     
                     # Delete .svg
                     await git_agent.delete_file(
                         file_path=svg_filename,
                         commit_message=f"docs: delete UML diagram for REQ-{existing['requirement_id']}",
                         branch=project.get("default_branch", "main")
                     )
                     
                     # Push changes
                     await git_agent.push_to_remote(branch=project.get("default_branch", "main"))
                     
        except Exception as e:
            logger.error(f"Failed to delete UML artifacts from Git: {e}")
            # Continue to delete from DB

        # Delete
        success = supabase.delete_uml_diagram(str(diagram_id), str(current_user.id))

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete diagram",
            )

        logger.info(f"UML diagram {diagram_id} deleted")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting UML diagram: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete UML diagram",
        )



@router.post("/uml/approve", response_model=ApproveUMLResponse)
async def approve_uml_diagram(
    request: ApproveUMLRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """
    Approve UML diagram and commit to GitHub.
    """
    supabase = SupabaseService()
    try:
        logger.info(f"Approving UML diagram {request.diagram_id}")

        # Get diagram
        diagram = supabase.get_uml_diagram(str(request.diagram_id), str(current_user.id))
        if not diagram:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="UML diagram not found or access denied",
            )

        # Get project
        project = await supabase.get_project(diagram["project_id"], str(current_user.id))
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )
        
        # Determine GitHub URL and repo details
        github_url = project.get("github_repo_url", "")
        if not github_url:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project does not have a GitHub repository URL"
            )

        try:
            # Remove .git extension and parse
            clean_url = github_url[:-4] if github_url.endswith(".git") else github_url
            parts = clean_url.split("/")
            # github_username = parts[-2] # Unused variable
            # repo_name = parts[-1]       # Unused variable
        except IndexError:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid GitHub URL format: {github_url}"
            )
            
        # Use local_path from project data
        repo_path = Path(project["local_path"])
        if not repo_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository not found at {repo_path}"
            )

        # Initialize Git Agent
        git_agent = GitAgent(str(repo_path))

        # 1. Save .puml file
        puml_filename = f"docs/uml/REQ-{diagram['requirement_id']}_class_diagram.puml"
        puml_content = diagram["plantuml_code"]
        
        await git_agent.commit_file(
            file_path=puml_filename,
            content=puml_content,
            commit_message=f"docs: add PlantUML source for REQ-{diagram['requirement_id']}",
            branch=request.branch
        )

        # 2. Save .svg file
        svg_filename = f"docs/uml/REQ-{diagram['requirement_id']}_class_diagram.svg"
        svg_content = diagram["rendered_svg"]
        
        # Function to commit and push
        commit_result = await git_agent.commit_file(
            file_path=svg_filename,
            content=svg_content,
            commit_message=request.commit_message, # Use user provided message for the main artifact
            branch=request.branch
        )

        # Push changes
        await git_agent.push_to_remote(request.branch)
        
        # Construct GitHub commit URL
        commit_url = f"{clean_url}/commit/{commit_result['sha']}"

        return ApproveUMLResponse(
            commit_sha=commit_result["sha"],
            commit_url=commit_url,
            file_path=svg_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving UML diagram: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve UML: {str(e)}",
        )


def _save_and_return_response(supabase, project_id, requirement_id, user_id, result):
    """Helper to save diagram and return response"""
    # Determine version
    latest_version = 0
    existing_diagrams = supabase.client.table("uml_diagrams").select("version").eq(
        "requirement_id", str(requirement_id)
    ).execute()
    
    if existing_diagrams.data:
        latest_version = max([d["version"] for d in existing_diagrams.data])

    new_diagram = {
        "project_id": str(project_id),
        "requirement_id": str(requirement_id),
        "user_id": str(user_id),
        "plantuml_code": result["plantuml_code"],
        "rendered_svg": result["rendered_svg"],
        "analysis_metadata": result["analysis"],
        "version": latest_version + 1,
        "diagram_type": "class",
    }

    data = supabase.create_uml_diagram(new_diagram)

    return _build_generation_response(data)


def _build_generation_response(diagram: dict) -> UMLGenerationResponse:
    """Build UMLGenerationResponse from diagram dict."""
    return UMLGenerationResponse(
        id=UUID(diagram["id"]),
        plantuml_code=diagram["plantuml_code"],
        svg_url=f"/api/uml/{diagram['id']}/render?format=svg",
        png_url=f"/api/uml/{diagram['id']}/render?format=png",
        analysis=diagram.get("analysis_metadata", {}),
        version=diagram.get("version", 1),
        created_at=diagram["created_at"],
    )
