from cryptography.fernet import Fernet
from config import settings
import base64
import logging

logger = logging.getLogger(__name__)

def get_encryption_key():
    """Get or generate encryption key"""
    # The ENCRYPTION_KEY in .env is already a base64-encoded Fernet key
    # Just encode it to bytes for Fernet
    return settings.ENCRYPTION_KEY.encode()

def encrypt_token(token: str) -> str:
    """Encrypt a token using Fernet encryption"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted_token = f.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted_token).decode()
    except Exception as e:
        logger.error(f"Error encrypting token: {e}")
        raise

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token using Fernet encryption"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decoded_token = base64.urlsafe_b64decode(encrypted_token.encode())
        decrypted_token = f.decrypt(decoded_token)
        return decrypted_token.decode()
    except Exception as e:
        logger.error(f"Error decrypting token: {e}")
        raise

def generate_encryption_key() -> str:
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return base64.urlsafe_b64encode(key).decode()