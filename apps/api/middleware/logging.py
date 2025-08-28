"""
Custom logging middleware for the ReliQuary API.
This middleware ensures all API interactions are logged in a structured format.
"""

import json
import time
import logging
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of API requests and responses"""
    
    def __init__(self, app: ASGIApp, logger: Optional[logging.Logger] = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger("reliquary.api")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log relevant information.
        
        Args:
            request: The incoming HTTP request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            The HTTP response
        """
        # Record start time
        start_time = time.time()
        
        # Extract request information
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        # Log the incoming request
        self.logger.info(f"Incoming request: {json.dumps(request_info)}")
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract response information
            response_info = {
                "status_code": response.status_code,
                "method": request.method,
                "url": str(request.url),
                "duration_ms": round(duration * 1000, 2),
                "client": request.client.host if request.client else "unknown"
            }
            
            # Log the response
            self.logger.info(f"Response: {json.dumps(response_info)}")
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log the error
            error_info = {
                "error": str(e),
                "method": request.method,
                "url": str(request.url),
                "duration_ms": round(duration * 1000, 2),
                "client": request.client.host if request.client else "unknown"
            }
            
            self.logger.error(f"Request error: {json.dumps(error_info)}")
            raise


# Convenience function to setup logging
def setup_api_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Setup structured logging for the API.
    
    Args:
        log_level: The logging level to use
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("reliquary.api")
    logger.setLevel(log_level)
    
    # Create console handler if it doesn't exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger