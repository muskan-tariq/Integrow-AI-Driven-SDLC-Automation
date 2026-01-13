from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
from datetime import datetime, timedelta
import logging

from config import settings
from services.supabase_service import supabase_service
from services.encryption import encrypt_token
from dependencies import create_access_token, get_current_user
from models.user import UserCreate, UserResponse, UserProfile
from services.audit_service import audit_service

logger = logging.getLogger(__name__)

router = APIRouter()

class GitHubCallbackRequest(BaseModel):
    code: str

class AuthResponse(BaseModel):
    access_token: str
    user: UserProfile

class LogoutResponse(BaseModel):
    status: str

@router.get("/github/callback", response_class=HTMLResponse)
async def github_callback_get(code: str):
    """Handle GitHub OAuth GET callback - sends code to Electron app"""
    # This endpoint receives the code from GitHub and sends it to the Electron app
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authenticating...</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .container {{
                text-align: center;
            }}
            .spinner {{
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Authenticating...</h1>
            <div class="spinner"></div>
            <p>Please wait while we complete your sign in.</p>
            <p><small>You can close this window.</small></p>
        </div>
        <script>
            // Send the code to the Electron app
            const code = '{code}';
            
            // Try to communicate with Electron
            if (window.opener) {{
                window.opener.postMessage({{ type: 'github-auth', code: code }}, '*');
                setTimeout(() => window.close(), 1000);
            }} else {{
                // If not opened by window.open, just display success
                setTimeout(() => {{
                    document.querySelector('.container').innerHTML = 
                        '<h1>✓ Authentication Successful</h1><p>You can close this window and return to the app.</p>';
                }}, 1000);
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/github/callback", response_model=AuthResponse)
async def github_callback(request: GitHubCallbackRequest, http_request: Request):
    """Handle GitHub OAuth callback"""
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": request.code,
                },
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = token_response.json()
            github_token = token_data.get("access_token")
            
            if not github_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received from GitHub"
                )
            
            # Get user profile from GitHub
            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {github_token}"}
            )
            
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user profile from GitHub"
                )
            
            github_user = user_response.json()
            
        # Encrypt the GitHub access token
        encrypted_token = encrypt_token(github_token)
        
        # Check if user exists
        existing_user = await supabase_service.get_user_by_github_id(str(github_user["id"]))
        
        if existing_user:
            # Update existing user
            user_data = {
                "github_username": github_user["login"],
                "email": github_user.get("email"),
                "avatar_url": github_user.get("avatar_url"),
                "access_token_encrypted": encrypted_token,
                "updated_at": datetime.utcnow().isoformat()
            }
            user = await supabase_service.update_user(existing_user["id"], user_data)
        else:
            # Create new user
            user_create_data = {
                "github_id": str(github_user["id"]),
                "github_username": github_user["login"],
                "email": github_user.get("email"),
                "avatar_url": github_user.get("avatar_url"),
                "access_token_encrypted": encrypted_token
            }
            user = await supabase_service.create_user(user_create_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or update user"
            )
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": user["id"], "github_username": user["github_username"]}
        )
        
        # Return auth response
        user_profile = UserProfile(
            id=user["id"],
            github_username=user["github_username"],
            email=user.get("email"),
            avatar_url=user.get("avatar_url"),
            github_id=user["github_id"],
            created_at=user["created_at"]
        )
        
        # Log successful login
        await audit_service.log_event(
            user_id=user["id"],
            action="user_login",
            details={
                "provider": "github",
                "github_username": user["github_username"]
            },
            ip_address=http_request.client.host if http_request.client else None
        )
        
        return AuthResponse(access_token=access_token, user=user_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: UserProfile = Depends(get_current_user)):
    """Logout user (token invalidation would be handled by client)"""
    # Log logout
    await audit_service.log_event(
        user_id=current_user.id,
        action="user_logout",
        details={"username": current_user.github_username}
    )
    
    # In a production system, you might want to blacklist the token
    # For now, we'll just return success
    return LogoutResponse(status="logged_out")