#!/usr/bin/env python3
"""
Utility script to generate encryption keys and setup environment
"""

import secrets
import string
from cryptography.fernet import Fernet
from pathlib import Path

def generate_jwt_secret(length=64):
    """Generate a secure JWT secret"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    """Generate a Fernet encryption key"""
    return Fernet.generate_key().decode()

def create_env_file():
    """Create .env file with generated secrets"""
    env_example_path = Path(".env.example")
    env_path = Path(".env")
    
    if not env_example_path.exists():
        print("❌ .env.example file not found")
        return
    
    if env_path.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Read template
    content = env_example_path.read_text()
    
    # Generate secrets
    jwt_secret = generate_jwt_secret()
    encryption_key = generate_encryption_key()
    
    # Replace placeholders
    content = content.replace("your_jwt_secret_key_here_should_be_long_and_random", jwt_secret)
    content = content.replace("your_fernet_encryption_key_here", encryption_key)
    
    # Write .env file
    env_path.write_text(content)
    
    print("✅ Generated .env file with secure secrets")
    print("\n🔐 Generated secrets:")
    print(f"   JWT Secret: {jwt_secret[:20]}...")
    print(f"   Encryption Key: {encryption_key[:20]}...")
    
    print("\n⚠️  Important:")
    print("   1. Update Supabase URLs and keys")
    print("   2. Update GitHub OAuth credentials")
    print("   3. Update PROJECTS_BASE_DIR path")
    print("   4. Never commit .env file to version control")

if __name__ == "__main__":
    print("🔑 InteGrow Environment Setup")
    print("=" * 40)
    create_env_file()