# auth/auth_middleware.py

import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from fastapi import FastAPI, Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi.responses import JSONResponse

from .oauth2 import verify_auth
from .rbac_enhanced import EnhancedRBACManager, ResourceType, Action
from .identity_manager import IdentityManager
from .jwt_tokens import jwt_manager
import config_package

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive authentication middleware that:
    - Validates JWT tokens and API keys
    - Manages session state
    - Provides security headers
    - Logs authentication events
    - Rate limiting (basic)
    """
    
    def __init__(
        self,
        app: FastAPI,
        excluded_paths: List[str] = None,
        require_auth_paths: List[str] = None,
        enable_rate_limiting: bool = True,
        max_requests_per_minute: int = 60
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/auth/info",
            "/auth/register",
            "/auth/token",
            "/auth/did/resolve",
            "/auth/webauthn/register/begin",
            "/auth/webauthn/authenticate/begin"
        ]
        self.require_auth_paths = require_auth_paths or [
            "/vaults",
            "/audit",
            "/auth/profile",
            "/auth/admin"
        ]
        self.enable_rate_limiting = enable_rate_limiting
        self.max_requests_per_minute = max_requests_per_minute
        self.rate_limit_storage = {}  # In production, use Redis
        
        # Initialize managers
        self.rbac_manager = EnhancedRBACManager()
        self.identity_manager = IdentityManager()
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request through authentication middleware"""
        start_time = time.time()
        
        # Add security headers
        response = None
        
        try:
            # Check if path is excluded from authentication
            if self._is_excluded_path(request.url.path):
                response = await call_next(request)
                return self._add_security_headers(response)
            
            # Rate limiting
            if self.enable_rate_limiting:
                if not self._check_rate_limit(request):
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"Maximum {self.max_requests_per_minute} requests per minute"
                        }
                    )
            
            # Authentication check
            auth_result = await self._authenticate_request(request)
            
            if auth_result["authenticated"]:
                # Add authentication context to request
                request.state.auth_context = auth_result["context"]
                request.state.user = auth_result.get("user")
                
                # Authorization check for protected paths
                if self._requires_auth(request.url.path):
                    if not await self._authorize_request(request, auth_result["context"]):
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={
                                "error": "Insufficient permissions",
                                "message": "Access denied for this resource"
                            }
                        )
            
            elif self._requires_auth(request.url.path):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": "Authentication required",
                        "message": "This endpoint requires authentication"
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Log successful request
            await self._log_request(request, response, start_time, auth_result)
            
            return self._add_security_headers(response)
            
        except HTTPException as e:
            # Handle HTTP exceptions
            response = JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
            return self._add_security_headers(response)
            
        except Exception as e:
            # Handle unexpected errors
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }
            )
            
            # Log error
            await self._log_error(request, e, start_time)
            
            return self._add_security_headers(response)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication"""
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False
    
    def _requires_auth(self, path: str) -> bool:
        """Check if path requires authentication"""
        for protected in self.require_auth_paths:
            if path.startswith(protected):
                return True
        return False
    
    def _check_rate_limit(self, request: Request) -> bool:
        """Basic rate limiting implementation"""
        if not self.enable_rate_limiting:
            return True
        
        # Get client identifier (IP address)
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        minute_ago = current_time - 60
        if client_ip in self.rate_limit_storage:
            self.rate_limit_storage[client_ip] = [
                timestamp for timestamp in self.rate_limit_storage[client_ip]
                if timestamp > minute_ago
            ]
        
        # Check rate limit
        if client_ip not in self.rate_limit_storage:
            self.rate_limit_storage[client_ip] = []
        
        if len(self.rate_limit_storage[client_ip]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.rate_limit_storage[client_ip].append(current_time)
        return True
    
    async def _authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate the incoming request"""
        auth_result = {
            "authenticated": False,
            "context": {},
            "user": None,
            "method": None
        }
        
        try:
            # Try to get authentication context
            auth_context = verify_auth(request)
            
            auth_result["authenticated"] = True
            auth_result["context"] = auth_context
            auth_result["method"] = auth_context.get("auth_type")
            
            # Get user information if available
            if auth_context.get("auth_type") == "oauth2":
                user_id = auth_context.get("user_id")
                username = auth_context.get("username")
                
                if username:
                    profile = self.identity_manager.get_user_profile(username)
                    if profile:
                        auth_result["user"] = profile
            
        except HTTPException:
            # Authentication failed, but this is not necessarily an error
            # Some endpoints may not require authentication
            pass
        except Exception as e:
            # Log unexpected authentication errors
            print(f"Authentication error: {e}")
        
        return auth_result
    
    async def _authorize_request(
        self, 
        request: Request, 
        auth_context: Dict[str, Any]
    ) -> bool:
        """Authorize the request based on RBAC"""
        try:
            # Basic authorization - can be extended with more sophisticated rules
            path = request.url.path
            method = request.method
            
            # Map HTTP methods to actions
            action_mapping = {
                "GET": Action.READ,
                "POST": Action.CREATE,
                "PUT": Action.UPDATE,
                "PATCH": Action.UPDATE,
                "DELETE": Action.DELETE
            }
            
            # Map paths to resources
            if path.startswith("/vaults"):
                resource_type = ResourceType.VAULT
            elif path.startswith("/audit"):
                resource_type = ResourceType.AUDIT_LOG
            elif path.startswith("/auth/profile"):
                resource_type = ResourceType.USER_PROFILE
            elif path.startswith("/auth/admin"):
                resource_type = ResourceType.SYSTEM_CONFIG
            else:
                # Default to allowing access for unmapped paths
                return True
            
            action = action_mapping.get(method, Action.READ)
            
            # Get principal information
            auth_type = auth_context.get("auth_type")
            if auth_type == "oauth2":
                principal_id = auth_context.get("user_id")
                principal_type = "user"
            elif auth_type == "api_key":
                principal_id = auth_context.get("client_name")
                principal_type = "client"
            else:
                return False
            
            if not principal_id:
                return False
            
            # Check permission
            granted, _ = self.rbac_manager.check_permission(
                principal_id=principal_id,
                principal_type=principal_type,
                resource_type=resource_type,
                action=action,
                context=auth_context
            )
            
            return granted
            
        except Exception as e:
            print(f"Authorization error: {e}")
            return False
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    async def _log_request(
        self,
        request: Request,
        response: Response,
        start_time: float,
        auth_result: Dict[str, Any]
    ):
        """Log request for audit purposes"""
        try:
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
            
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "status_code": response.status_code,
                "duration_ms": duration,
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "authenticated": auth_result["authenticated"],
                "auth_method": auth_result.get("method"),
                "user_id": auth_result.get("context", {}).get("user_id"),
                "username": auth_result.get("context", {}).get("username")
            }
            
            # In production, send to proper logging system
            print(f"REQUEST_LOG: {json.dumps(log_entry)}")
            
        except Exception as e:
            print(f"Logging error: {e}")
    
    async def _log_error(self, request: Request, error: Exception, start_time: float):
        """Log errors for debugging"""
        try:
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            
            error_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "ERROR",
                "method": request.method,
                "path": str(request.url.path),
                "error": str(error),
                "error_type": type(error).__name__,
                "duration_ms": duration,
                "client_ip": request.client.host
            }
            
            print(f"ERROR_LOG: {json.dumps(error_entry)}")
            
        except Exception as e:
            print(f"Error logging error: {e}")

class CORSMiddleware:
    """
    Simple CORS middleware for ReliQuary authentication.
    In production, use fastapi.middleware.cors.CORSMiddleware with proper configuration.
    """
    
    def __init__(
        self,
        app: FastAPI,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None
    ):
        self.app = app
        self.allow_origins = allow_origins or ["*"]  # Configure properly in production
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or [
            "Authorization",
            "Content-Type", 
            "X-API-Key",
            "X-Requested-With"
        ]
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Handle CORS preflight and add CORS headers"""
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            return self._add_cors_headers(response, request)
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers to response
        return self._add_cors_headers(response, request)
    
    def _add_cors_headers(self, response: Response, request: Request) -> Response:
        """Add CORS headers to response"""
        origin = request.headers.get("origin")
        
        if origin and (origin in self.allow_origins or "*" in self.allow_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
        
        return response

def setup_auth_middleware(app: FastAPI) -> FastAPI:
    """
    Setup authentication middleware for FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Configured FastAPI application
    """
    # Add authentication middleware
    app.add_middleware(
        AuthenticationMiddleware,
        excluded_paths=[
            "/docs",
            "/redoc",
            "/openapi.json", 
            "/health",
            "/auth/info",
            "/auth/register",
            "/auth/token",
            "/auth/refresh",
            "/auth/did/resolve",
            "/auth/webauthn/register/begin",
            "/auth/webauthn/authenticate/begin",
            "/"
        ],
        require_auth_paths=[
            "/vaults",
            "/audit", 
            "/auth/profile",
            "/auth/admin",
            "/auth/webauthn/register/complete",
            "/auth/webauthn/authenticate/complete",
            "/auth/did/register"
        ],
        enable_rate_limiting=True,
        max_requests_per_minute=100
    )
    
    # Add CORS middleware if needed
    # Uncomment and configure for production
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["https://yourfrontend.com"],
    #     allow_methods=["GET", "POST", "PUT", "DELETE"],
    #     allow_headers=["Authorization", "Content-Type", "X-API-Key"]
    # )
    
    return app

if __name__ == "__main__":
    print("--- Testing Authentication Middleware ---")
    
    # This would be used in your main FastAPI app like this:
    print("""
To use the authentication middleware in your FastAPI app:

from fastapi import FastAPI
from auth.auth_middleware import setup_auth_middleware
from auth.auth_endpoints import auth_router

app = FastAPI(title="ReliQuary API", version="2.0.0")

# Setup authentication middleware
app = setup_auth_middleware(app)

# Include authentication endpoints
app.include_router(auth_router)

# Your other routers...
""")
    
    print("✅ Authentication middleware configured!")