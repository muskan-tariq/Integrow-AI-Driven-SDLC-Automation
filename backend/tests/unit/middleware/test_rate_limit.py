"""
Test cases for Rate Limit Middleware
"""
import sys
import os

# Add backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, backend_dir)

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from config import settings

# Import app after path setup
from main import app

client = TestClient(app)


class TestRateLimitMiddleware:
    """Test suite for rate limiting middleware"""
    
    def test_request_allowed_under_limit(self):
        """Test that requests are allowed when under the rate limit"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_rate_limit_exceeded(self):
        """Test that requests are blocked when rate limit is exceeded"""
        # Temporarily set a very low limit for testing
        original_limit = settings.RATE_LIMIT_REQUESTS
        original_window = settings.RATE_LIMIT_WINDOW
        
        try:
            # Set limit to 5 requests per 60 seconds
            settings.RATE_LIMIT_REQUESTS = 5
            settings.RATE_LIMIT_WINDOW = 60
            
            # Clear the rate limit store to start fresh
            from middleware.rate_limit import rate_limit_store
            rate_limit_store.clear()
            
            # Make requests up to the limit
            for i in range(5):
                response = client.get("/health")
                assert response.status_code == 200, f"Request {i+1} should succeed"
            
            # The 6th request should be rate limited
            response = client.get("/health")
            assert response.status_code == 429, "Request should be rate limited"
            assert response.json()["detail"] == "Too many requests"
            
        finally:
            # Restore original settings
            settings.RATE_LIMIT_REQUESTS = original_limit
            settings.RATE_LIMIT_WINDOW = original_window
            rate_limit_store.clear()
    
    def test_rate_limit_window_reset(self):
        """Test that rate limit resets after window expires"""
        from middleware.rate_limit import rate_limit_store
        import time
        
        original_limit = settings.RATE_LIMIT_REQUESTS
        original_window = settings.RATE_LIMIT_WINDOW
        
        try:
            # Set a very short window for testing (1 second)
            settings.RATE_LIMIT_REQUESTS = 2
            settings.RATE_LIMIT_WINDOW = 1
            rate_limit_store.clear()
            
            # Make 2 requests (hit the limit)
            for _ in range(2):
                response = client.get("/health")
                assert response.status_code == 200
            
            # 3rd request should be blocked
            response = client.get("/health")
            assert response.status_code == 429
            
            # Wait for window to reset
            time.sleep(1.1)
            
            # Request should now succeed
            response = client.get("/health")
            assert response.status_code == 200
            
        finally:
            settings.RATE_LIMIT_REQUESTS = original_limit
            settings.RATE_LIMIT_WINDOW = original_window
            rate_limit_store.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
