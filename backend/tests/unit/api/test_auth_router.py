"""
Unit tests for Auth Router - GitHub OAuth, JWT validation, user profile endpoints.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

# Import modules under test
from api.auth_router import router, GitHubCallbackRequest, AuthResponse, LogoutResponse
from models.user import UserProfile
from dependencies import create_access_token, verify_token


class TestGitHubCallback:
    """Tests for GitHub OAuth callback endpoints."""

    @pytest.fixture
    def mock_github_token_response(self):
        """Mock successful GitHub token exchange."""
        return {"access_token": "gho_mocktoken12345"}

    @pytest.fixture
    def mock_github_user_response(self):
        """Mock successful GitHub user profile."""
        return {
            "id": 12345,
            "login": "testuser",
            "email": "test@example.com",
            "avatar_url": "https://avatars.githubusercontent.com/u/12345"
        }

    @pytest.mark.asyncio
    async def test_github_callback_success(self, mock_github_token_response, mock_github_user_response):
        """Test successful GitHub OAuth callback."""
        from api.auth_router import github_callback
        
        # Create a mock request with both code and client attributes
        request = MagicMock()
        request.code = "valid_code_123"
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        
        with patch('api.auth_router.httpx.AsyncClient') as mock_client:
            # Setup mock responses
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock token exchange
            mock_token_resp = MagicMock()
            mock_token_resp.status_code = 200
            mock_token_resp.json.return_value = mock_github_token_response
            
            # Mock user profile fetch
            mock_user_resp = MagicMock()
            mock_user_resp.status_code = 200
            mock_user_resp.json.return_value = mock_github_user_response
            
            mock_instance.post.return_value = mock_token_resp
            mock_instance.get.return_value = mock_user_resp
            
            with patch('api.auth_router.supabase_service') as mock_supabase:
                with patch('api.auth_router.encrypt_token', return_value="encrypted_token"):
                    with patch('api.auth_router.create_access_token', return_value="jwt_token"):
                        with patch('api.auth_router.audit_service') as mock_audit:
                            mock_audit.log_event = AsyncMock()
                            # Mock user doesn't exist, create new
                            mock_supabase.get_user_by_github_id = AsyncMock(return_value=None)
                            mock_supabase.create_user = AsyncMock(return_value={
                                "id": str(uuid.uuid4()),
                                "github_id": "12345",
                                "github_username": "testuser",
                                "email": "test@example.com",
                                "avatar_url": "https://avatars.githubusercontent.com/u/12345",
                                "created_at": datetime.utcnow().isoformat()
                            })
                            
                            response = await github_callback(request)
                            
                            assert response.access_token == "jwt_token"
                            assert response.user.github_username == "testuser"

    @pytest.mark.asyncio
    async def test_github_callback_invalid_code(self):
        """Test GitHub callback with invalid authorization code."""
        from api.auth_router import github_callback
        
        request = GitHubCallbackRequest(code="invalid_code")
        
        with patch('api.auth_router.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock failed token exchange
            mock_resp = MagicMock()
            mock_resp.status_code = 401
            mock_instance.post.return_value = mock_resp
            
            with pytest.raises(HTTPException) as exc_info:
                await github_callback(request)
            
            assert exc_info.value.status_code == 400
            assert "Failed to exchange code" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_github_callback_no_token_received(self):
        """Test GitHub callback when no access token is returned."""
        from api.auth_router import github_callback
        
        request = GitHubCallbackRequest(code="code_without_token")
        
        with patch('api.auth_router.httpx.AsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            
            # Mock response without access_token
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"error": "bad_verification_code"}
            mock_instance.post.return_value = mock_resp
            
            with pytest.raises(HTTPException) as exc_info:
                await github_callback(request)
            
            assert exc_info.value.status_code == 400
            assert "No access token" in str(exc_info.value.detail)


class TestUserProfile:
    """Tests for user profile endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        return UserProfile(
            id=str(uuid.uuid4()),
            github_id="12345",
            github_username="testuser",
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg",
            created_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_get_current_user_profile_success(self, mock_user):
        """Test getting current user profile with valid auth."""
        from api.auth_router import get_current_user_profile
        
        result = await get_current_user_profile(current_user=mock_user)
        
        assert result.github_username == "testuser"
        assert result.email == "test@example.com"
        assert result.id == mock_user.id


class TestLogout:
    """Tests for logout endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock authenticated user."""
        return UserProfile(
            id=str(uuid.uuid4()),
            github_id="12345",
            github_username="testuser",
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg",
            created_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_logout_success(self, mock_user):
        """Test successful logout returns correct status."""
        from api.auth_router import logout
        
        with patch('api.auth_router.audit_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            result = await logout(current_user=mock_user)
        
        assert isinstance(result, LogoutResponse)
        assert result.status == "logged_out"


class TestJWTToken:
    """Tests for JWT token creation and verification."""

    def test_create_access_token_contains_subject(self):
        """Test that created token contains the subject claim."""
        data = {"sub": "user-123", "github_username": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify the token can be decoded
        payload = verify_token(token)
        assert payload["sub"] == "user-123"
        assert payload["github_username"] == "testuser"

    def test_create_access_token_with_custom_expiry(self):
        """Test token creation with custom expiration."""
        data = {"sub": "user-123"}
        expires = timedelta(hours=2)
        token = create_access_token(data, expires_delta=expires)
        
        payload = verify_token(token)
        assert payload["sub"] == "user-123"
        assert "exp" in payload

    def test_verify_token_invalid_token(self):
        """Test that invalid token raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401

    def test_verify_token_missing_subject(self):
        """Test that token without subject raises HTTPException."""
        from jose import jwt
        from config import settings
        
        # Create token without 'sub' claim
        token = jwt.encode(
            {"data": "no_subject"},
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401


class TestGitHubCallbackRequest:
    """Tests for GitHubCallbackRequest model."""

    def test_valid_request(self):
        """Test creating valid callback request."""
        request = GitHubCallbackRequest(code="abc123")
        assert request.code == "abc123"

    def test_request_requires_code(self):
        """Test that code is required."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            GitHubCallbackRequest()
