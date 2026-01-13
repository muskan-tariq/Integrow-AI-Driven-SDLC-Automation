"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing"""
    monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
    monkeypatch.setenv('SUPABASE_KEY', 'test_supabase_key')
    monkeypatch.setenv('SUPABASE_SERVICE_KEY', 'test_service_key')
    monkeypatch.setenv('GITHUB_CLIENT_ID', 'test_client_id')
    monkeypatch.setenv('GITHUB_CLIENT_SECRET', 'test_client_secret')
    monkeypatch.setenv('JWT_SECRET', 'test_jwt_secret_key_minimum_32_characters_long')
    monkeypatch.setenv('ENCRYPTION_KEY', 'test_encryption_key_base64_encoded_32_bytes_minimum')


@pytest.fixture
def sample_user():
    """Provide a sample user for testing"""
    return {
        'id': 'user-123',
        'github_id': '12345',
        'github_username': 'testuser',
        'email': 'test@example.com',
        'avatar_url': 'https://example.com/avatar.jpg'
    }


@pytest.fixture
def sample_project():
    """Provide a sample project for testing"""
    return {
        'id': 'project-123',
        'user_id': 'user-123',
        'name': 'test-project',
        'description': 'A test project',
        'local_path': 'E:\\Projects\\test-project',
        'github_repo_url': 'https://github.com/testuser/test-project',
        'github_repo_id': '98765',
        'visibility': 'private',
        'template': 'blank',
        'status': 'active'
    }


@pytest.fixture
def valid_jwt_token():
    """Provide a valid JWT token for testing"""
    # This is a mock token for testing
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyJ9.test'
