"""
Unit tests for Config module - Settings and configuration.
"""
import pytest
from config import Settings, settings, get_settings


class TestSettings:
    """Unit tests for Settings configuration."""

    def test_settings_instance_exists(self):
        """Test that settings singleton exists."""
        assert settings is not None

    def test_get_settings_returns_settings(self):
        """Test that get_settings returns the settings instance."""
        result = get_settings()
        assert result is settings

    def test_settings_has_environment(self):
        """Test that settings has environment configuration."""
        assert hasattr(settings, 'ENVIRONMENT')
        assert settings.ENVIRONMENT in ['development', 'production', 'test']

    def test_settings_has_host_and_port(self):
        """Test that settings has host and port configuration."""
        assert hasattr(settings, 'HOST')
        assert hasattr(settings, 'PORT')
        assert isinstance(settings.PORT, int)

    def test_settings_has_cors_origins(self):
        """Test that settings has CORS configuration."""
        assert hasattr(settings, 'ALLOWED_ORIGINS')
        assert isinstance(settings.ALLOWED_ORIGINS, list)
        assert len(settings.ALLOWED_ORIGINS) > 0

    def test_settings_has_supabase_config(self):
        """Test that settings has Supabase configuration."""
        assert hasattr(settings, 'SUPABASE_URL')
        assert hasattr(settings, 'SUPABASE_KEY')

    def test_settings_has_github_oauth_config(self):
        """Test that settings has GitHub OAuth configuration."""
        assert hasattr(settings, 'GITHUB_CLIENT_ID')
        assert hasattr(settings, 'GITHUB_CLIENT_SECRET')
        assert hasattr(settings, 'GITHUB_REDIRECT_URI')

    def test_settings_has_jwt_config(self):
        """Test that settings has JWT configuration."""
        assert hasattr(settings, 'JWT_SECRET')
        assert hasattr(settings, 'JWT_ALGORITHM')
        assert settings.JWT_ALGORITHM == "HS256"
        assert hasattr(settings, 'JWT_EXPIRATION_HOURS')
        assert settings.JWT_EXPIRATION_HOURS > 0

    def test_settings_has_encryption_key(self):
        """Test that settings has encryption key."""
        assert hasattr(settings, 'ENCRYPTION_KEY')
        assert len(settings.ENCRYPTION_KEY) > 0

    def test_settings_has_projects_base_dir(self):
        """Test that settings has projects directory configuration."""
        assert hasattr(settings, 'PROJECTS_BASE_DIR')
        assert len(settings.PROJECTS_BASE_DIR) > 0

    def test_settings_has_redis_url(self):
        """Test that settings has Redis configuration."""
        assert hasattr(settings, 'REDIS_URL')
        assert settings.REDIS_URL.startswith('redis://')

    def test_settings_has_rate_limit_config(self):
        """Test that settings has rate limiting configuration."""
        assert hasattr(settings, 'RATE_LIMIT_REQUESTS')
        assert hasattr(settings, 'RATE_LIMIT_WINDOW')
        assert settings.RATE_LIMIT_REQUESTS > 0
        assert settings.RATE_LIMIT_WINDOW > 0

    def test_settings_has_llm_api_keys(self):
        """Test that settings has LLM API key configuration."""
        assert hasattr(settings, 'GROQ_API_KEY')
        assert hasattr(settings, 'GEMINI_API_KEY')
        assert hasattr(settings, 'OPENAI_API_KEY')

    def test_settings_has_feature_flags(self):
        """Test that settings has feature flag configuration."""
        assert hasattr(settings, 'USE_LOCAL_SPACY')
        assert hasattr(settings, 'ENABLE_CACHE')
        assert hasattr(settings, 'CACHE_TTL_HOURS')
        assert isinstance(settings.USE_LOCAL_SPACY, bool)
        assert isinstance(settings.ENABLE_CACHE, bool)

    def test_settings_jwt_expiration_default(self):
        """Test JWT expiration default value."""
        assert settings.JWT_EXPIRATION_HOURS == 24

    def test_settings_rate_limit_defaults(self):
        """Test rate limit default values."""
        assert settings.RATE_LIMIT_REQUESTS == 100
        assert settings.RATE_LIMIT_WINDOW == 60

    def test_settings_cache_ttl_default(self):
        """Test cache TTL default value."""
        assert settings.CACHE_TTL_HOURS == 24
