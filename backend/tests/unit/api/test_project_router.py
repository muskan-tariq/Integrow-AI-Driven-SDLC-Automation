"""
Unit tests for Project Router - Model validation and business logic.
"""
import pytest
from datetime import datetime
import uuid

# Import modules under test
from models.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectVisibility, ProjectStatus, ProjectTemplate
)
from models.user import UserProfile


class TestProjectModels:
    """Tests for project Pydantic models and validation."""

    def test_project_create_valid(self):
        """Test creating a valid project."""
        project = ProjectCreate(
            name="my-project",
            description="A test project",
            visibility=ProjectVisibility.PRIVATE
        )
        assert project.name == "my-project"
        assert project.visibility == ProjectVisibility.PRIVATE

    def test_project_create_name_validation_alphanumeric(self):
        """Test that project name only allows alphanumeric and hyphens."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(name="my project")  # Space not allowed
        
        assert "alphanumeric" in str(exc_info.value).lower()

    def test_project_create_name_no_leading_hyphen(self):
        """Test that project name cannot start with hyphen."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(name="-my-project")
        
        assert "hyphen" in str(exc_info.value).lower()

    def test_project_create_name_no_trailing_hyphen(self):
        """Test that project name cannot end with hyphen."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(name="my-project-")
        
        assert "hyphen" in str(exc_info.value).lower()

    def test_project_create_empty_name(self):
        """Test that empty name is rejected."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ProjectCreate(name="")

    def test_project_update_optional_fields(self):
        """Test that all update fields are optional."""
        update = ProjectUpdate()
        assert update.name is None
        assert update.description is None
        assert update.visibility is None
        assert update.status is None

    def test_project_update_partial(self):
        """Test partial project update."""
        update = ProjectUpdate(name="new-name")
        assert update.name == "new-name"
        assert update.description is None

    def test_project_visibility_enum(self):
        """Test project visibility enum values."""
        assert ProjectVisibility.PUBLIC == "public"
        assert ProjectVisibility.PRIVATE == "private"

    def test_project_status_enum(self):
        """Test project status enum values."""
        assert ProjectStatus.ACTIVE == "active"
        assert ProjectStatus.ARCHIVED == "archived"

    def test_project_template_enum(self):
        """Test project template enum values."""
        assert ProjectTemplate.BLANK == "blank"
        assert ProjectTemplate.WEB_APP == "web-app"
        assert ProjectTemplate.MOBILE_APP == "mobile-app"
        assert ProjectTemplate.API == "api"

    def test_project_name_with_numbers(self):
        """Test project name with numbers is valid."""
        project = ProjectCreate(name="project123")
        assert project.name == "project123"

    def test_project_name_with_hyphens(self):
        """Test project name with hyphens in middle is valid."""
        project = ProjectCreate(name="my-cool-project")
        assert project.name == "my-cool-project"

    def test_project_create_with_template(self):
        """Test creating project with specific template."""
        project = ProjectCreate(
            name="api-project",
            template=ProjectTemplate.API
        )
        assert project.template == ProjectTemplate.API

    def test_project_create_default_visibility(self):
        """Test default visibility is private."""
        project = ProjectCreate(name="test-project")
        assert project.visibility == ProjectVisibility.PRIVATE

    def test_project_create_default_template(self):
        """Test default template is blank."""
        project = ProjectCreate(name="test-project")
        assert project.template == ProjectTemplate.BLANK

    def test_project_update_status_change(self):
        """Test updating project status."""
        update = ProjectUpdate(status=ProjectStatus.ARCHIVED)
        assert update.status == ProjectStatus.ARCHIVED

    def test_project_update_visibility_change(self):
        """Test updating project visibility."""
        update = ProjectUpdate(visibility=ProjectVisibility.PUBLIC)
        assert update.visibility == ProjectVisibility.PUBLIC

    def test_project_name_max_length(self):
        """Test project name max length validation."""
        # 100 characters should work
        long_name = "a" * 100
        project = ProjectCreate(name=long_name)
        assert len(project.name) == 100

    def test_project_description_optional(self):
        """Test project description is optional."""
        project = ProjectCreate(name="test-project")
        assert project.description is None

    def test_project_with_description(self):
        """Test project with description."""
        project = ProjectCreate(
            name="test-project",
            description="A detailed description of the project"
        )
        assert project.description == "A detailed description of the project"
