import sys
import os
import asyncio

# Add backend to path (parent of tests directory)
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from fastapi.testclient import TestClient
from main import app
from config import settings
from services.audit_service import audit_service

def test_security_configuration():
    print("\n--- Verifying Configuration ---")
    print(f"DEBUG Mode: {settings.DEBUG}")
    print(f"Environment: {settings.ENVIRONMENT}")
    
    if not settings.DEBUG and settings.ENVIRONMENT == "production":
        print("✅ Configuration verified: Secure defaults active.")
    else:
        print("❌ Configuration verification FAILED: Insecure defaults detected.")

def test_security_headers():
    print("\n--- Verifying Security Headers ---")
    client = TestClient(app)
    response = client.get("/health")
    
    headers = response.headers
    required_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    all_passed = True
    for header, value in required_headers.items():
        if headers.get(header) == value:
            print(f"✅ {header}: Present and correct")
        else:
            print(f"❌ {header}: MISSING or Incorrect. Got: {headers.get(header)}")
            all_passed = False
            
    if all_passed:
        print("✅ All security headers verified.")

async def test_audit_logging():
    print("\n--- Verifying Audit Service ---")
    try:
        # Attempt to log a test event
        await audit_service.log_event(
            user_id="00000000-0000-0000-0000-000000000000",
            action="verification_test",
            details={"status": "running checks"}
        )
        print("✅ AuditService.log_event executed without raising exceptions.")
    except Exception as e:
        print(f"❌ AuditService check failed: {e}")

if __name__ == "__main__":
    print("Starting Security Verification...")
    test_security_configuration()
    test_security_headers()
    asyncio.run(test_audit_logging())
    print("\nVerification Complete.")
