"""
Integration tests for Services - testing interface boundaries.
"""
import pytest
from unittest.mock import patch, MagicMock
from services.encryption import encrypt_token, decrypt_token
from services.plantuml_service import PlantUMLService

class TestEncryptionServiceIntegration:
    """Integration tests for encryption service."""
    
    def test_token_encryption_roundtrip(self):
        """Test full encryption/decryption cycle."""
        original_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        
        # Encrypt
        encrypted = encrypt_token(original_token)
        assert encrypted != original_token
        
        # Decrypt
        decrypted = decrypt_token(encrypted)
        assert decrypted == original_token
        
    def test_different_tokens_produce_different_ciphertexts(self):
        """Test encryption validation."""
        token1 = "aaa"
        token2 = "bbb"
        
        enc1 = encrypt_token(token1)
        enc2 = encrypt_token(token2)
        
        assert enc1 != enc2


class TestPlantUMLIntegration:
    """Integration tests for PlantUML service."""

    @pytest.fixture
    def plantuml_service(self):
        return PlantUMLService()

