"""
Unit tests for Pydantic Models - User, Project, Requirement, UML Diagram.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

# Import actual models
from models.user import UserBase, UserCreate, UserUpdate, UserResponse, UserProfile
from models.project import (
    ProjectVisibility, ProjectStatus, ProjectTemplate,
    ProjectBase, ProjectCreate, ProjectUpdate, Project, ProjectResponse
)


class TestUserModels:
    """Unit tests for User model validation."""

    def test_user_base_valid(self):
        """Test valid UserBase creation."""
        user = UserBase(
            github_username="testuser",
            email="test@example.com",
            avatar_url="https://github.com/avatar.png"
        )
        assert user.github_username == "testuser"
        assert user.email == "test@example.com"

    def test_user_base_requires_username(self):
        """Test that github_username is required."""
        with pytest.raises(ValidationError):
            UserBase()

    def test_user_base_username_min_length(self):
        """Test username minimum length validation."""
        with pytest.raises(ValidationError):
            UserBase(github_username="")

    def test_user_base_username_max_length(self):
        """Test username maximum length validation (39 chars for GitHub)."""
        with pytest.raises(ValidationError):
            UserBase(github_username="a" * 40)

    def test_user_base_optional_email(self):
        """Test that email is optional."""
        user = UserBase(github_username="testuser")
        assert user.email is None

    def test_user_base_email_validation(self):
        """Test email format validation."""
        with pytest.raises(ValidationError):
            UserBase(github_username="testuser", email="invalid-email")

    def test_user_create_valid(self):
        """Test valid UserCreate with required fields."""
        user = UserCreate(
            github_username="testuser",
            github_id="12345",
            access_token_encrypted="encrypted_token_here"
        )
        assert user.github_id == "12345"
        assert user.access_token_encrypted == "encrypted_token_here"

    def test_user_create_requires_github_id(self):
        """Test that github_id is required."""
        with pytest.raises(ValidationError):
            UserCreate(
                github_username="testuser",
                access_token_encrypted="token"
            )

    def test_user_update_all_optional(self):
        """Test that all UserUpdate fields are optional."""
        update = UserUpdate()
        assert update.github_username is None
        assert update.email is None

    def test_user_response_valid(self):
        """Test valid UserResponse creation."""
        now = datetime.now()
        user = UserResponse(
            id="uuid-123",
            github_id="12345",
            github_username="testuser",
            created_at=now,
            updated_at=now
        )
        assert user.id == "uuid-123"


class TestProjectModels:
    """Unit tests for Project model validation."""

    def test_project_visibility_enum(self):
        """Test ProjectVisibility enum values."""
        assert ProjectVisibility.PUBLIC == "public"
        assert ProjectVisibility.PRIVATE == "private"

    def test_project_status_enum(self):
        """Test ProjectStatus enum values."""
        assert ProjectStatus.ACTIVE == "active"
        assert ProjectStatus.ARCHIVED == "archived"

    def test_project_template_enum(self):
        """Test ProjectTemplate enum values."""
        assert ProjectTemplate.BLANK == "blank"
        assert ProjectTemplate.WEB_APP == "web-app"

    def test_project_base_valid(self):
        """Test valid ProjectBase creation."""
        project = ProjectBase(name="my-project")
        assert project.name == "my-project"
        assert project.visibility == ProjectVisibility.PRIVATE

    def test_project_base_requires_name(self):
        """Test that project name is required."""
        with pytest.raises(ValidationError):
            ProjectBase()

    def test_project_name_validation_alphanumeric(self):
        """Test that project name only allows alphanumeric and hyphens."""
        with pytest.raises(ValidationError):
            ProjectBase(name="invalid name!")

    def test_project_name_cannot_start_with_hyphen(self):
        """Test that project name cannot start with hyphen."""
        with pytest.raises(ValidationError):
            ProjectBase(name="-invalid")

    def test_project_name_cannot_end_with_hyphen(self):
        """Test that project name cannot end with hyphen."""
        with pytest.raises(ValidationError):
            ProjectBase(name="invalid-")

    def test_project_create_inherits_base(self):
        """Test that ProjectCreate inherits from ProjectBase."""
        project = ProjectCreate(name="new-project")
        assert project.name == "new-project"

    def test_project_update_all_optional(self):
        """Test that all ProjectUpdate fields are optional."""
        update = ProjectUpdate()
        assert update.name is None
        assert update.description is None

    def test_project_response_valid(self):
        """Test valid ProjectResponse creation."""
        now = datetime.now()
        project = ProjectResponse(
            id="uuid-123",
            user_id="user-456",
            name="test-project",
            local_path="/path/to/project",
            github_repo_url="https://github.com/user/repo",
            github_username="testuser",
            repo_name="repo",
            created_at=now,
            updated_at=now
        )
        assert project.id == "uuid-123"
        assert project.default_branch == "main"
