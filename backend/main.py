from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
from contextlib import asynccontextmanager

from config import settings
from api import auth_router, project_router, user_router, requirements_router
from api import user_stories_router, uml_router, code_generation_router, dashboard_router, review_router, debt_router
from services.supabase_service import supabase_client

# Security
security = HTTPBearer()

# Security Headers Middleware
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting InteGrow Backend...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Supabase URL: {settings.SUPABASE_URL}")
    
    # Test database connection
    try:
        response = supabase_client.table('users').select('count').execute()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down InteGrow Backend...")

# Create FastAPI app
app = FastAPI(
    title="InteGrow Backend API",
    description="AI-driven Software Engineering Suite Backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
from middleware.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

# Security Headers
app.middleware("http")(security_headers_middleware)

# Include routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router.router, prefix="/api/users", tags=["Users"])
app.include_router(project_router.router, prefix="/api/projects", tags=["Projects"])
app.include_router(requirements_router.router, tags=["Requirements"])
app.include_router(user_stories_router.router, tags=["User Stories"])
app.include_router(uml_router.router, tags=["UML Diagrams"])
app.include_router(code_generation_router.router, tags=["Code Generation"])
app.include_router(dashboard_router.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(review_router.router)
app.include_router(debt_router.router)

@app.get("/")
async def root():
    return {
        "message": "InteGrow Backend API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        response = supabase_client.table('users').select('count').execute()
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": response.data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )