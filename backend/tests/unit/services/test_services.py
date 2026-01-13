"""
Unit tests for Services - Encryption, PlantUML, LLM services.
"""
import pytest
from unittest.mock import patch, MagicMock

# Import actual services
from services.encryption import encrypt_token, decrypt_token, generate_encryption_key


class TestEncryptionService:
    """Unit tests for token encryption/decryption."""

    def test_encrypt_token_returns_string(self):
        """Test that encrypt_token returns a string."""
        encrypted = encrypt_token("test_token")
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0

    def test_decrypt_token_returns_original(self):
        """Test that decrypt_token returns the original token."""
        original = "my_secret_token_12345"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        assert decrypted == original

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypted token can be decrypted correctly."""
        tokens = ["short", "medium_length_token", "very_long_token_with_special_chars_!@#$%"]
        for token in tokens:
            encrypted = encrypt_token(token)
            decrypted = decrypt_token(encrypted)
            assert decrypted == token

    def test_encrypted_token_is_different(self):
        """Test that encrypted token is different from original."""
        original = "my_token"
        encrypted = encrypt_token(original)
        assert encrypted != original

    def test_generate_encryption_key(self):
        """Test that generate_encryption_key returns a valid key."""
        key = generate_encryption_key()
        assert isinstance(key, str)
        assert len(key) > 0

    def test_different_tokens_produce_different_encryptions(self):
        """Test that different tokens produce different encrypted values."""
        token1 = "token_one"
        token2 = "token_two"
        encrypted1 = encrypt_token(token1)
        encrypted2 = encrypt_token(token2)
        assert encrypted1 != encrypted2


class TestPlantUMLService:
    """Unit tests for PlantUML diagram generation."""

    def test_plantuml_service_exists(self):
        """Test that PlantUML service module can be imported."""
        from services import plantuml_service
        assert plantuml_service is not None


class TestLLMService:
    """Unit tests for LLM service interactions."""

    def test_llm_service_exists(self):
        """Test that LLM service module can be imported."""
        from services import llm_service
        assert llm_service is not None
