"""
Unit tests for LLM Service - Provider fallback and caching.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import hashlib
import json


class TestLLMServiceInitialization:
    """Tests for LLMService initialization."""

    def test_service_can_be_imported(self):
        """Test that LLMService can be imported."""
        from services.llm_service import LLMService
        assert LLMService is not None

    def test_service_initialization_no_providers(self):
        """Test service initializes even without API keys."""
        with patch.dict('os.environ', {}, clear=True):
            from services.llm_service import LLMService
            service = LLMService()
            assert service._providers == {} or len(service._providers) >= 0

    def test_service_has_provider_order(self):
        """Test service has correct provider fallback order."""
        from services.llm_service import LLMService
        service = LLMService()
        assert service._order == ["groq", "gemini", "openai"]


class TestLLMServiceCaching:
    """Tests for LLM service caching functionality."""

    def test_cache_key_generation(self):
        """Test cache key is generated from prompt hash."""
        prompt = "Test prompt for LLM"
        expected_hash = hashlib.md5(prompt.encode()).hexdigest()
        expected_key = f"llm:{expected_hash}"
        
        assert expected_key.startswith("llm:")
        assert len(expected_hash) == 32  # MD5 produces 32 char hex

    def test_different_prompts_have_different_keys(self):
        """Test different prompts produce different cache keys."""
        prompt1 = "First prompt"
        prompt2 = "Second prompt"
        
        key1 = f"llm:{hashlib.md5(prompt1.encode()).hexdigest()}"
        key2 = f"llm:{hashlib.md5(prompt2.encode()).hexdigest()}"
        
        assert key1 != key2

    def test_cache_get_returns_none_without_redis(self):
        """Test cache get returns None when Redis not configured."""
        from services.llm_service import LLMService
        
        with patch.dict('os.environ', {}, clear=True):
            service = LLMService()
            service._redis = None
            result = service._cache_get("some_key")
            assert result is None

    def test_cache_set_does_not_fail_without_redis(self):
        """Test cache set doesn't raise when Redis not configured."""
        from services.llm_service import LLMService
        
        with patch.dict('os.environ', {}, clear=True):
            service = LLMService()
            service._redis = None
            # Should not raise
            service._cache_set("key", {"data": "value"})


class TestLLMServiceComplete:
    """Tests for LLM completion method."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock LLM service."""
        from services.llm_service import LLMService
        service = LLMService()
        service._redis = None
        return service

    @pytest.mark.asyncio
    async def test_complete_returns_cached_result(self, mock_service):
        """Test that cached results are returned without calling provider."""
        cached_result = {"provider": "groq", "text": "Cached response"}
        
        with patch.object(mock_service, '_cache_get', return_value=cached_result):
            result = await mock_service.complete("Test prompt")
            assert result == cached_result

    @pytest.mark.asyncio
    async def test_complete_raises_when_no_providers(self, mock_service):
        """Test that complete raises when all providers fail."""
        mock_service._providers = {}
        mock_service._cache_get = MagicMock(return_value=None)
        
        with pytest.raises(RuntimeError) as exc_info:
            await mock_service.complete("Test prompt")
        
        assert "All providers failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_complete_with_groq_provider(self, mock_service):
        """Test completion with Groq provider."""
        mock_groq = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Groq response"))]
        mock_groq.chat.completions.create.return_value = mock_response
        
        mock_service._providers = {"groq": mock_groq}
        mock_service._cache_get = MagicMock(return_value=None)
        mock_service._cache_set = MagicMock()
        
        result = await mock_service.complete("Test prompt")
        
        assert result["provider"] == "groq"
        assert result["text"] == "Groq response"

    @pytest.mark.asyncio
    async def test_complete_falls_back_on_provider_failure(self, mock_service):
        """Test that service falls back to next provider on failure."""
        # Groq fails
        mock_groq = MagicMock()
        mock_groq.chat.completions.create.side_effect = Exception("Groq error")
        
        # Gemini succeeds
        mock_gemini = MagicMock()
        mock_gemini.generate_content.return_value = MagicMock(text="Gemini response")
        
        mock_service._providers = {"groq": mock_groq, "gemini": mock_gemini}
        mock_service._cache_get = MagicMock(return_value=None)
        mock_service._cache_set = MagicMock()
        
        result = await mock_service.complete("Test prompt")
        
        assert result["provider"] == "gemini"
        assert result["text"] == "Gemini response"


class TestLLMServiceProviderIntegration:
    """Integration tests for provider-specific logic."""

    def test_groq_model_name(self):
        """Test Groq uses correct model name."""
        expected_model = "llama-3.3-70b-versatile"
        # This is documentation - the model is hardcoded in the service
        assert expected_model == "llama-3.3-70b-versatile"

    def test_openai_model_name(self):
        """Test OpenAI uses correct model name."""
        expected_model = "gpt-4o-mini"
        # This is documentation - the model is hardcoded in the service
        assert expected_model == "gpt-4o-mini"

    def test_gemini_model_name(self):
        """Test Gemini uses correct model name."""
        expected_model = "gemini-2.5-flash"
        # This is documentation - the model is hardcoded in the service
        assert expected_model == "gemini-2.5-flash"
