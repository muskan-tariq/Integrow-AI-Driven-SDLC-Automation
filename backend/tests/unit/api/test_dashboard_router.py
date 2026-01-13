"""
Unit tests for Dashboard Router - Model validation tests.
"""
import pytest
from datetime import datetime
import uuid

# Import modules under test
from api.dashboard_router import DashboardStats, RecentActivity, DashboardResponse


class TestDashboardModels:
    """Tests for dashboard Pydantic models."""

    def test_dashboard_stats_creation(self):
        """Test creating DashboardStats with all fields."""
        stats = DashboardStats(
            total_projects=5,
            total_requirements=10,
            total_user_stories=25,
            total_uml_diagrams=8,
            total_code_sessions=3,
            total_generated_files=15,
            projects_change=2,
            requirements_change=3,
            stories_change=5
        )
        assert stats.total_projects == 5
        assert stats.total_requirements == 10
        assert stats.projects_change == 2

    def test_dashboard_stats_defaults(self):
        """Test DashboardStats default values."""
        stats = DashboardStats(
            total_projects=0,
            total_requirements=0,
            total_user_stories=0,
            total_uml_diagrams=0,
            total_code_sessions=0,
            total_generated_files=0
        )
        assert stats.projects_change == 0
        assert stats.requirements_change == 0
        assert stats.stories_change == 0

    def test_recent_activity_creation(self):
        """Test creating RecentActivity."""
        activity = RecentActivity(
            id=str(uuid.uuid4()),
            type="project_created",
            title="New Project",
            description="Created project test-app",
            timestamp=datetime.utcnow().isoformat(),
            project_name="test-app"
        )
        assert activity.type == "project_created"
        assert activity.title == "New Project"

    def test_recent_activity_optional_project_name(self):
        """Test RecentActivity without project name."""
        activity = RecentActivity(
            id=str(uuid.uuid4()),
            type="user_login",
            title="User Login",
            description="User logged in",
            timestamp=datetime.utcnow().isoformat()
        )
        assert activity.project_name is None

    def test_dashboard_response_creation(self):
        """Test creating full DashboardResponse."""
        stats = DashboardStats(
            total_projects=1,
            total_requirements=2,
            total_user_stories=5,
            total_uml_diagrams=1,
            total_code_sessions=0,
            total_generated_files=3
        )
        activities = [
            RecentActivity(
                id=str(uuid.uuid4()),
                type="project_created",
                title="New Project",
                description="Created project",
                timestamp=datetime.utcnow().isoformat()
            )
        ]
        response = DashboardResponse(stats=stats, recent_activity=activities)
        assert response.stats.total_projects == 1
        assert len(response.recent_activity) == 1

    def test_dashboard_stats_zero_values(self):
        """Test DashboardStats with zero values (new user)."""
        stats = DashboardStats(
            total_projects=0,
            total_requirements=0,
            total_user_stories=0,
            total_uml_diagrams=0,
            total_code_sessions=0,
            total_generated_files=0
        )
        assert stats.total_projects == 0
        assert stats.total_user_stories == 0

    def test_dashboard_response_empty_activities(self):
        """Test DashboardResponse with empty activity list."""
        stats = DashboardStats(
            total_projects=0,
            total_requirements=0,
            total_user_stories=0,
            total_uml_diagrams=0,
            total_code_sessions=0,
            total_generated_files=0
        )
        response = DashboardResponse(stats=stats, recent_activity=[])
        assert len(response.recent_activity) == 0

    def test_activity_types_are_strings(self):
        """Test that activity types are strings."""
        activity = RecentActivity(
            id="123",
            type="requirement_analyzed",
            title="Analysis Complete",
            description="Analyzed requirement",
            timestamp="2024-01-01T00:00:00"
        )
        assert isinstance(activity.type, str)
        assert isinstance(activity.title, str)
