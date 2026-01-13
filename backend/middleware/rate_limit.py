from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from config import settings
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# In-memory store for rate limiting (simple fixed window)
# Structure: {client_ip: {"count": int, "window_start": float}}
rate_limit_store = defaultdict(lambda: {"count": 0, "window_start": 0.0})

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Identify client by IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0]

        current_time = time.time()
        window = settings.RATE_LIMIT_WINDOW
        limit = settings.RATE_LIMIT_REQUESTS
        
        client_data = rate_limit_store[client_ip]
        
        # Reset window if expired
        if current_time - client_data["window_start"] > window:
            client_data["count"] = 0
            client_data["window_start"] = current_time
        
        # Check limit
        if client_data["count"] >= limit:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests"}
            )
        
        # Increment counter
        client_data["count"] += 1
        
        return await call_next(request)
