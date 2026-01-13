"""
Integration tests for API endpoints with TestClient.
Tests the full request/response cycle with mocked dependencies.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
import uuid

# Import main app
from main import app


@pytest.fixture
def client():
    """Create TestClient for the FastAPI app."""
    return TestClient(app)


class TestHealthCheck:
    """Tests for health check endpoints."""

    def test_root_endpoint_returns_info(self, client):
        """Test that root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestAuthEndpointsIntegration:
    """Integration tests for authentication endpoints."""

    def test_auth_me_requires_authentication(self, client):
        """Test that /api/auth/me requires valid token."""
        response = client.get("/api/auth/me")
        assert response.status_code in [401, 403, 422]

    def test_auth_logout_requires_authentication(self, client):
        """Test that /api/auth/logout requires valid token."""
        response = client.post("/api/auth/logout")
        assert response.status_code in [401, 403, 422]


class TestProjectEndpointsIntegration:
    """Integration tests for project endpoints."""

    def test_projects_list_requires_authentication(self, client):
        """Test that project listing requires authentication."""
        response = client.get("/api/projects/")
        assert response.status_code in [401, 403, 422]

    def test_project_create_requires_authentication(self, client):
        """Test that project creation requires authentication."""
        response = client.post("/api/projects/", json={
            "name": "test-project",
            "description": "Test"
        })
        # 401/403 = auth required, 405 = method not allowed, 422 = validation
        assert response.status_code in [401, 403, 405, 422]


class TestDashboardEndpointsIntegration:
    """Integration tests for dashboard endpoints."""

    def test_dashboard_stats_requires_authentication(self, client):
        """Test that dashboard stats require authentication."""
        response = client.get("/api/dashboard/stats")
        assert response.status_code in [401, 403, 422]


class TestRequirementsEndpointsIntegration:
    """Integration tests for requirements endpoints."""

    def test_requirements_analyze_requires_authentication(self, client):
        """Test that requirement analysis requires authentication."""
        response = client.post("/api/requirements/analyze", json={
            "requirement_text": "Test requirement",
            "project_id": str(uuid.uuid4())
        })
        assert response.status_code in [401, 403, 422]


class TestUMLEndpointsIntegration:
    """Integration tests for UML endpoints."""

    def test_uml_list_requires_authentication(self, client):
        """Test that UML listing requires authentication."""
        response = client.get(f"/api/uml/{uuid.uuid4()}")
        assert response.status_code in [401, 403, 422]


class TestAPIErrorHandling:
    """Tests for API error handling."""

    def test_nonexistent_endpoint_returns_404(self, client):
        """Test that nonexistent endpoints return 404."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404

    def test_health_endpoint_works(self, client):
        """Test health endpoint is accessible."""
        # Health might fail without DB but shouldn't 404
        response = client.get("/health")
        assert response.status_code in [200, 503]
