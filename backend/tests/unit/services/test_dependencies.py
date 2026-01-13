"""
Unit tests for Dependencies module - JWT tokens and authentication.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from fastapi import HTTPException
from jose import jwt

# Import dependencies
from dependencies import create_access_token, verify_token
from config import settings


class TestCreateAccessToken:
    """Tests for JWT token creation."""

    def test_create_access_token_basic(self):
        """Test creating a basic access token."""
        data = {"sub": "user-123", "github_username": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Test creating token with custom expiry."""
        data = {"sub": "user-123"}
        expires = timedelta(hours=1)
        token = create_access_token(data, expires_delta=expires)
        
        assert token is not None

    def test_create_access_token_payload(self):
        """Test that token contains correct payload."""
        data = {"sub": "user-456", "github_username": "myuser"}
        token = create_access_token(data)
        
        # Decode and verify
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == "user-456"
        assert payload["github_username"] == "myuser"
        assert "exp" in payload

    def test_create_access_token_includes_expiry(self):
        """Test that token includes expiry claim."""
        data = {"sub": "user-789"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert "exp" in payload

    def test_create_access_token_different_data(self):
        """Test that different data produces different tokens."""
        token1 = create_access_token({"sub": "user-1"})
        token2 = create_access_token({"sub": "user-2"})
        
        assert token1 != token2


class TestVerifyToken:
    """Tests for JWT token verification."""

    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        data = {"sub": "user-123"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "user-123"

    def test_verify_token_returns_payload(self):
        """Test that verify_token returns full payload."""
        data = {"sub": "user-456", "github_username": "testuser"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert "sub" in payload
        assert "exp" in payload

    def test_verify_invalid_token_raises(self):
        """Test that invalid token raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401

    def test_verify_malformed_token_raises(self):
        """Test that malformed token raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("not-a-jwt")
        
        assert exc_info.value.status_code == 401

    def test_verify_token_wrong_secret_raises(self):
        """Test that token with wrong secret raises HTTPException."""
        # Create token with wrong secret
        wrong_token = jwt.encode(
            {"sub": "user-123", "exp": 9999999999},
            "wrong-secret",
            algorithm="HS256"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(wrong_token)
        
        assert exc_info.value.status_code == 401

    def test_verify_token_missing_sub_raises(self):
        """Test that token without 'sub' claim raises HTTPException."""
        # Create token without sub
        token = jwt.encode(
            {"exp": 9999999999},  # No "sub" field
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401


class TestTokenRoundtrip:
    """Integration tests for token create/verify cycle."""

    def test_create_and_verify_roundtrip(self):
        """Test that created token can be verified."""
        original_data = {"sub": "test-user-id", "github_username": "testuser"}
        
        token = create_access_token(original_data)
        payload = verify_token(token)
        
        assert payload["sub"] == original_data["sub"]
        assert payload["github_username"] == original_data["github_username"]

    def test_multiple_tokens_roundtrip(self):
        """Test multiple token create/verify cycles."""
        users = [
            {"sub": "user-1", "github_username": "user1"},
            {"sub": "user-2", "github_username": "user2"},
            {"sub": "user-3", "github_username": "user3"},
        ]
        
        for user_data in users:
            token = create_access_token(user_data)
            payload = verify_token(token)
            assert payload["sub"] == user_data["sub"]
