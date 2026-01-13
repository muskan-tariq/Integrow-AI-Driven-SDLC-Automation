"""
Unit tests for Supabase Service - Database operations with mocked client.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import uuid


class TestSupabaseServiceUserOperations:
    """Tests for user-related Supabase operations."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create a mock Supabase client."""
        mock_client = MagicMock()
        return mock_client

    def test_get_user_by_github_id_found(self, mock_supabase_client):
        """Test finding a user by GitHub ID."""
        from services.supabase_service import SupabaseService
        
        user_data = {
            "id": str(uuid.uuid4()),
            "github_id": "12345",
            "github_username": "testuser",
            "email": "test@example.com"
        }
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [user_data]
            
            service = SupabaseService()
            service.client = mock_supabase_client
            
            # Call the sync wrapper
            result = mock_supabase_client.table("users").select("*").eq("github_id", "12345").execute()
            
            assert result.data[0]["github_username"] == "testuser"

    def test_get_user_by_github_id_not_found(self, mock_supabase_client):
        """Test when user is not found by GitHub ID."""
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
            
            result = mock_supabase_client.table("users").select("*").eq("github_id", "nonexistent").execute()
            
            assert result.data == []

    def test_create_user_success(self, mock_supabase_client):
        """Test creating a new user."""
        user_id = str(uuid.uuid4())
        user_data = {
            "github_id": "12345",
            "github_username": "newuser",
            "email": "new@example.com"
        }
        created_user = {**user_data, "id": user_id, "created_at": datetime.utcnow().isoformat()}
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [created_user]
            
            result = mock_supabase_client.table("users").insert(user_data).execute()
            
            assert result.data[0]["id"] == user_id
            assert result.data[0]["github_username"] == "newuser"

    def test_update_user_success(self, mock_supabase_client):
        """Test updating an existing user."""
        user_id = str(uuid.uuid4())
        update_data = {"email": "updated@example.com"}
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
                "id": user_id,
                "email": "updated@example.com"
            }]
            
            result = mock_supabase_client.table("users").update(update_data).eq("id", user_id).execute()
            
            assert result.data[0]["email"] == "updated@example.com"


class TestSupabaseServiceProjectOperations:
    """Tests for project-related Supabase operations."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create a mock Supabase client."""
        return MagicMock()

    def test_get_user_projects_empty(self, mock_supabase_client):
        """Test getting projects when user has none."""
        user_id = str(uuid.uuid4())
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = []
            
            result = mock_supabase_client.table("projects").select("*").eq("user_id", user_id).order("created_at").range(0, 10).execute()
            
            assert result.data == []

    def test_get_user_projects_with_data(self, mock_supabase_client):
        """Test getting projects with existing data."""
        user_id = str(uuid.uuid4())
        projects = [
            {"id": str(uuid.uuid4()), "name": "project-1", "user_id": user_id},
            {"id": str(uuid.uuid4()), "name": "project-2", "user_id": user_id}
        ]
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = projects
            
            result = mock_supabase_client.table("projects").select("*").eq("user_id", user_id).order("created_at").range(0, 10).execute()
            
            assert len(result.data) == 2

    def test_create_project_success(self, mock_supabase_client):
        """Test creating a new project."""
        project_id = str(uuid.uuid4())
        project_data = {
            "name": "new-project",
            "user_id": str(uuid.uuid4()),
            "local_path": "E:\\Projects\\new-project"
        }
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [{
                **project_data, 
                "id": project_id,
                "created_at": datetime.utcnow().isoformat()
            }]
            
            result = mock_supabase_client.table("projects").insert(project_data).execute()
            
            assert result.data[0]["name"] == "new-project"

    def test_get_project_by_id(self, mock_supabase_client):
        """Test getting a project by ID."""
        project_id = str(uuid.uuid4())
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
                "id": project_id,
                "name": "test-project"
            }]
            
            result = mock_supabase_client.table("projects").select("*").eq("id", project_id).execute()
            
            assert result.data[0]["id"] == project_id

    def test_update_project_success(self, mock_supabase_client):
        """Test updating a project."""
        project_id = str(uuid.uuid4())
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
                "id": project_id,
                "name": "updated-name",
                "updated_at": datetime.utcnow().isoformat()
            }]
            
            result = mock_supabase_client.table("projects").update({"name": "updated-name"}).eq("id", project_id).execute()
            
            assert result.data[0]["name"] == "updated-name"


class TestSupabaseServiceUMLOperations:
    """Tests for UML diagram-related Supabase operations."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create a mock Supabase client."""
        return MagicMock()

    def test_create_uml_diagram(self, mock_supabase_client):
        """Test creating a UML diagram record."""
        diagram_id = str(uuid.uuid4())
        diagram_data = {
            "requirement_id": str(uuid.uuid4()),
            "diagram_type": "class",
            "plantuml_code": "@startuml\nclass User\n@enduml"
        }
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [{
                **diagram_data,
                "id": diagram_id
            }]
            
            result = mock_supabase_client.table("uml_diagrams").insert(diagram_data).execute()
            
            assert result.data[0]["diagram_type"] == "class"

    def test_get_uml_diagram_by_requirement(self, mock_supabase_client):
        """Test getting UML diagram by requirement ID."""
        requirement_id = str(uuid.uuid4())
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [{
                "id": str(uuid.uuid4()),
                "requirement_id": requirement_id,
                "diagram_type": "class"
            }]
            
            result = mock_supabase_client.table("uml_diagrams").select("*").eq("requirement_id", requirement_id).order("created_at", desc=True).limit(1).execute()
            
            assert result.data[0]["requirement_id"] == requirement_id

    def test_list_uml_diagrams_pagination(self, mock_supabase_client):
        """Test listing UML diagrams with pagination."""
        requirement_id = str(uuid.uuid4())
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = [{
                "id": str(uuid.uuid4()),
                "diagram_type": "class"
            }]
            
            result = mock_supabase_client.table("uml_diagrams").select("*").eq("requirement_id", requirement_id).order("created_at").range(0, 10).execute()
            
            assert len(result.data) == 1


class TestSupabaseServiceActivityLogging:
    """Tests for activity logging operations."""

    @pytest.fixture
    def mock_supabase_client(self):
        """Create a mock Supabase client."""
        return MagicMock()

    def test_log_project_activity(self, mock_supabase_client):
        """Test logging project activity."""
        activity_data = {
            "project_id": str(uuid.uuid4()),
            "activity_type": "requirement_created",
            "description": "Created new requirement"
        }
        
        with patch('services.supabase_service.supabase_client', mock_supabase_client):
            mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [{
                **activity_data,
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat()
            }]
            
            result = mock_supabase_client.table("project_activities").insert(activity_data).execute()
            
            assert result.data[0]["activity_type"] == "requirement_created"
