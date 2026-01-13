from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging

from dependencies import get_current_user
from models.user import UserProfile
from services.supabase_service import supabase_service

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardStats(BaseModel):
    total_projects: int
    total_requirements: int
    total_user_stories: int
    total_uml_diagrams: int
    total_code_sessions: int
    total_generated_files: int
    total_reviews: int = 0
    total_debt_sessions: int = 0
    total_test_cases: int = 0
    # Weekly changes (can be negative)
    projects_change: int = 0
    requirements_change: int = 0
    stories_change: int = 0


class RecentActivity(BaseModel):
    id: str
    type: str  # 'project', 'requirement', 'story', 'uml', 'code'
    title: str
    description: str
    timestamp: str
    project_name: Optional[str] = None


class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_activity: list[RecentActivity]


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    current_user: UserProfile = Depends(get_current_user)
):
    """Get dashboard statistics for the current user"""
    try:
        user_id = str(current_user.id)
        
        # Get total counts
        projects_result = supabase_service.client.table("projects").select("id", count="exact").eq("user_id", user_id).execute()
        total_projects = projects_result.count or 0
        
        # Get project IDs for this user
        project_ids = [p["id"] for p in projects_result.data] if projects_result.data else []
        
        # Count requirements for user's projects
        total_requirements = 0
        total_user_stories = 0
        total_uml_diagrams = 0
        total_code_sessions = 0
        total_generated_files = 0
        total_reviews = 0
        total_debt_sessions = 0
        total_test_cases = 0
        
        if project_ids:
            # Requirements count
            for pid in project_ids:
                reqs = supabase_service.client.table("requirements").select("id", count="exact").eq("project_id", pid).execute()
                total_requirements += reqs.count or 0
            
            # User stories count (through requirements)
            req_result = supabase_service.client.table("requirements").select("id").in_("project_id", project_ids).execute()
            req_ids = [r["id"] for r in req_result.data] if req_result.data else []
            
            if req_ids:
                for rid in req_ids:
                    stories = supabase_service.client.table("user_stories").select("id", count="exact").eq("requirement_id", rid).execute()
                    total_user_stories += stories.count or 0
            
            # UML diagrams count
            for pid in project_ids:
                uml = supabase_service.client.table("uml_diagrams").select("id", count="exact").eq("project_id", pid).execute()
                total_uml_diagrams += uml.count or 0
            
            # Code generation sessions count
            for pid in project_ids:
                sessions = supabase_service.client.table("code_generation_sessions").select("id", count="exact").eq("project_id", pid).execute()
                total_code_sessions += sessions.count or 0
            
            # Generated files count
            session_result = supabase_service.client.table("code_generation_sessions").select("id").in_("project_id", project_ids).execute()
            session_ids = [s["id"] for s in session_result.data] if session_result.data else []
            
            if session_ids:
                for sid in session_ids:
                    files = supabase_service.client.table("generated_files").select("id", count="exact").eq("session_id", sid).execute()
                    total_generated_files += files.count or 0
            
            # Code reviews count
            reviews = supabase_service.client.table("review_sessions").select("id", count="exact").in_("project_id", project_ids).execute()
            total_reviews = reviews.count or 0
            
            # Technical debt sessions count
            debt = supabase_service.client.table("debt_sessions").select("id", count="exact").in_("project_id", project_ids).execute()
            total_debt_sessions = debt.count or 0
        
        # Calculate weekly changes (simplified - just count items from last 7 days)
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        projects_this_week = supabase_service.client.table("projects").select("id", count="exact").eq("user_id", user_id).gte("created_at", week_ago).execute()
        projects_change = projects_this_week.count or 0
        
        requirements_change = 0
        stories_change = 0
        
        if project_ids:
            for pid in project_ids:
                reqs_week = supabase_service.client.table("requirements").select("id", count="exact").eq("project_id", pid).gte("created_at", week_ago).execute()
                requirements_change += reqs_week.count or 0
        
        # Build stats
        stats = DashboardStats(
            total_projects=total_projects,
            total_requirements=total_requirements,
            total_user_stories=total_user_stories,
            total_uml_diagrams=total_uml_diagrams,
            total_code_sessions=total_code_sessions,
            total_generated_files=total_generated_files,
            total_reviews=total_reviews,
            total_debt_sessions=total_debt_sessions,
            total_test_cases=total_test_cases,
            projects_change=projects_change,
            requirements_change=requirements_change,
            stories_change=stories_change,
        )
        
        # Get recent activity
        recent_activity = []
        
        # 1. Recent projects (limit 5)
        recent_projects = supabase_service.client.table("projects")\
            .select("id, name, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()
            
        if recent_projects.data:
            for p in recent_projects.data:
                recent_activity.append(RecentActivity(
                    id=p["id"],
                    type="project",
                    title="New project created",
                    description=p.get("name", "Unnamed"),
                    timestamp=p.get("created_at", ""),
                    project_name=p.get("name")
                ))
        
        # 2. Recent requirements (limit 5)
        # First get project map for names
        project_map = {p["id"]: p.get("name") for p in projects_result.data} if projects_result.data else {}
        
        if project_ids:
            recent_reqs = supabase_service.client.table("requirements")\
                .select("id, project_id, created_at")\
                .in_("project_id", project_ids)\
                .order("created_at", desc=True)\
                .limit(5)\
                .execute()
                
            if recent_reqs.data:
                for r in recent_reqs.data:
                    p_name = project_map.get(r["project_id"], "Unknown Project")
                    recent_activity.append(RecentActivity(
                        id=r["id"],
                        type="requirement",
                        title="Requirements added",
                        description=f"New requirement analyzed",
                        timestamp=r.get("created_at", ""),
                        project_name=p_name
                    ))

        # Sort combined activity by timestamp (most recent first)
        recent_activity.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 3. Recent UML diagrams (limit 5)
        if project_ids:
            recent_uml = supabase_service.client.table("uml_diagrams")\
                .select("id, project_id, diagram_type, created_at")\
                .in_("project_id", project_ids)\
                .order("created_at", desc=True)\
                .limit(5)\
                .execute()
                
            if recent_uml.data:
                for u in recent_uml.data:
                    p_name = project_map.get(u["project_id"], "Unknown Project")
                    recent_activity.append(RecentActivity(
                        id=u["id"],
                        type="uml",
                        title="UML Diagram generated",
                        description=f"{u.get('diagram_type', 'Class')} diagram created",
                        timestamp=u.get("created_at", ""),
                        project_name=p_name
                    ))
        
        # 4. Recent code generation sessions (limit 5)
        if project_ids:
            recent_code = supabase_service.client.table("code_generation_sessions")\
                .select("id, project_id, status, created_at")\
                .in_("project_id", project_ids)\
                .order("created_at", desc=True)\
                .limit(5)\
                .execute()
                
            if recent_code.data:
                for c in recent_code.data:
                    p_name = project_map.get(c["project_id"], "Unknown Project")
                    status_text = "completed" if c.get("status") == "completed" else "started"
                    recent_activity.append(RecentActivity(
                        id=c["id"],
                        type="code",
                        title="Code generation " + status_text,
                        description=f"Code generation session {status_text}",
                        timestamp=c.get("created_at", ""),
                        project_name=p_name
                    ))
        
        # 5. Recent user stories (limit 5)
        if req_ids:
            recent_stories = supabase_service.client.table("user_stories")\
                .select("id, requirement_id, title, created_at")\
                .in_("requirement_id", req_ids)\
                .order("created_at", desc=True)\
                .limit(5)\
                .execute()
                
            if recent_stories.data:
                # Get requirement to project mapping
                req_to_project = {}
                if req_result.data:
                    for r in req_result.data:
                        req_to_project[r["id"]] = r.get("project_id")
                
                for s in recent_stories.data:
                    req_id = s.get("requirement_id")
                    proj_id = req_to_project.get(req_id)
                    p_name = project_map.get(proj_id, "Unknown Project") if proj_id else "Unknown Project"
                    recent_activity.append(RecentActivity(
                        id=s["id"],
                        type="story",
                        title="User story created",
                        description=s.get("title", "New user story")[:50],
                        timestamp=s.get("created_at", ""),
                        project_name=p_name
                    ))

        # 6. Recent code reviews (limit 5)
        if project_ids:
            recent_reviews = supabase_service.client.table("review_sessions")\
                .select("id, project_id, version, score, created_at")\
                .in_("project_id", project_ids)\
                .order("created_at", desc=True)\
                .limit(5)\
                .execute()
                
            if recent_reviews.data:
                for r in recent_reviews.data:
                    p_name = project_map.get(r["project_id"], "Unknown Project")
                    recent_activity.append(RecentActivity(
                        id=r["id"],
                        type="review",
                        title=f"Code review V{r['version']}",
                        description=f"Quality Score: {r['score']}/100",
                        timestamp=r.get("created_at", ""),
                        project_name=p_name
                    ))

        # 7. Recent technical debt analysis (limit 5)
        if project_ids:
            recent_debt = supabase_service.client.table("debt_sessions")\
                .select("id, project_id, version, overall_score, total_issues, created_at")\
                .in_("project_id", project_ids)\
                .order("created_at", desc=True)\
                .limit(5)\
                .execute()
                
            if recent_debt.data:
                for d in recent_debt.data:
                    p_name = project_map.get(d["project_id"], "Unknown Project")
                    recent_activity.append(RecentActivity(
                        id=d["id"],
                        type="debt",
                        title=f"Technical Debt V{d['version']}",
                        description=f"Score: {d['overall_score']}/100, {d['total_issues']} issues",
                        timestamp=d.get("created_at", ""),
                        project_name=p_name
                    ))

        # Re-sort combined activity by timestamp (most recent first)
        recent_activity.sort(key=lambda x: x.timestamp, reverse=True)
        
        return DashboardResponse(
            stats=stats,
            recent_activity=recent_activity[:10]
        )
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
        )
