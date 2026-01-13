import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from models.generated_code import ApproveCodeRequest, ApproveCodeResponse
from models.user import UserProfile
from api.code_generation_router import approve_code_generation

@pytest.fixture
def mock_supabase_service():
    with patch("api.code_generation_router.supabase_service") as mock:
        yield mock

@pytest.fixture
def mock_git_agent():
    with patch("agents.integration.git_agent.GitAgent") as mock:
        # Define async methods on the instance mock
        instance = mock.return_value
        instance.commit_multiple_files = AsyncMock()
        instance.push_to_remote = AsyncMock()
        instance.repo = MagicMock() # Mock repo attribute if needed
        yield mock

@pytest.fixture
def current_user():
    from datetime import datetime
    return UserProfile(
        id=str(uuid4()),
        github_username="testuser",
        email="test@example.com",
        github_id="12345",
        created_at=datetime.utcnow(),
        avatar_url="https://example.com/avatar.png"
    )

@pytest.mark.asyncio
async def test_approve_code_success(mock_supabase_service, current_user):
    # Setup Data
    project_id = uuid4()
    session_id = uuid4()
    
    # Mock DB Responses via side_effect with caching
    table_mocks = {}

    def table_side_effect(table_name):
        if table_name in table_mocks:
            return table_mocks[table_name]

        mock_query = MagicMock()
        mock_execute = MagicMock()
        # Allow chaining
        mock_query.select.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.order.return_value = mock_query
        mock_query.update.return_value = mock_query
        mock_query.execute.return_value = mock_execute
        
        if table_name == "code_generation_sessions":
            mock_execute.data = [{
                "id": str(session_id),
                "user_id": current_user.id,
                "project_id": str(project_id),
                "approved_at": None
            }]
        elif table_name == "generated_files":
            mock_execute.data = [
                {"file_path": "models/user.py", "content": "class User: ..."}
            ]
        else:
            mock_execute.data = []
            
        table_mocks[table_name] = mock_query
        return mock_query

    mock_supabase_service.client.table.side_effect = table_side_effect
    
    # Mock get_project method
    mock_supabase_service.get_project.return_value = {
        "id": str(project_id),
        "local_path": "/tmp/test-repo",
        "github_repo_url": "https://github.com/test/repo.git"
    }

    # Mock GitAgent - patch at source since it's imported locally in the function
    with patch("agents.integration.git_agent.GitAgent") as mock_git_cls:
        mock_git_instance = mock_git_cls.return_value
        mock_git_instance.commit_multiple_files = AsyncMock(return_value={
            "sha": "abc1234",
            "files_committed": 1
        })
        mock_git_instance.push_to_remote = AsyncMock(return_value=True)

        # Mock Path
        with patch("pathlib.Path") as mock_path_cls:
            mock_path_instance = mock_path_cls.return_value
            # Configure path operations to return mocks that work
            mock_path_instance.__truediv__.return_value = mock_path_instance
            mock_path_instance.exists.return_value = True
            
            # Execute Endpoint
            request = ApproveCodeRequest(
                session_id=session_id,
                commit_message="feat: add user model",
                branch="feature/user-auth"
            )
            
            response = await approve_code_generation(request, current_user)

            # Verification
            assert isinstance(response, ApproveCodeResponse)
            assert response.commit_sha == "abc1234"
            assert response.branch == "feature/user-auth"
            assert response.files_committed == 1
            
            # Check pushes
            mock_git_instance.push_to_remote.assert_called_with("feature/user-auth")
            
            # Check that table was accessed for update (via cached mock)
            assert "code_generation_sessions" in table_mocks

@pytest.mark.asyncio
async def test_approve_code_already_approved(mock_supabase_service, current_user):
    session_id = uuid4()
    
    # Mock Session with existing approval
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": str(session_id),
        "user_id": current_user.id,
        "approved_at": "2024-01-01T12:00:00Z"
    }]

    request = ApproveCodeRequest(session_id=session_id, commit_message="test")
    
    with pytest.raises(HTTPException) as exc:
        await approve_code_generation(request, current_user)
    
    assert exc.value.status_code == 400
    assert "already approved" in exc.value.detail

@pytest.mark.asyncio
async def test_approve_code_unauthorized(mock_supabase_service, current_user):
    session_id = uuid4()
    other_user_id = uuid4()
    
    # Mock Session belonging to another user
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": str(session_id),
        "user_id": other_user_id
    }]

    request = ApproveCodeRequest(session_id=session_id, commit_message="test")
    
    with pytest.raises(HTTPException) as exc:
        await approve_code_generation(request, current_user)
    
    assert exc.value.status_code == 403
