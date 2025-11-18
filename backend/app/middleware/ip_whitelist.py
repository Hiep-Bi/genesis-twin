"""IP Whitelist Middleware - Restrict access to specific IPs/networks"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import List
import ipaddress
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware to restrict access based on IP whitelist"""
    
    def __init__(self, app, allowed_ips: List[str] = None, allowed_networks: List[str] = None):
        super().__init__(app)
        self.allowed_ips = allowed_ips or getattr(settings, 'ALLOWED_IPS', [])
        self.allowed_networks = allowed_networks or getattr(settings, 'ALLOWED_NETWORKS', [])
        self.compiled_networks = []
        
        # Compile network ranges for faster lookup
        for network in self.allowed_networks:
            try:
                self.compiled_networks.append(ipaddress.ip_network(network, strict=False))
            except ValueError as e:
                logger.warning(f"Invalid network range {network}: {e}")
    
    def is_allowed_ip(self, client_ip: str) -> bool:
        """Check if client IP is allowed"""
        try:
            # Check exact IP match
            if client_ip in self.allowed_ips:
                return True
            
            # Check network ranges
            client_ip_obj = ipaddress.ip_address(client_ip)
            for network in self.compiled_networks:
                if client_ip_obj in network:
                    return True
            
            return False
        except ValueError as e:
            logger.warning(f"Invalid IP address {client_ip}: {e}")
            return False
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next):
        """Process request and check IP whitelist"""
        # Skip IP check for health check and docs endpoints
        path = request.url.path
        skip_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        
        if any(path.startswith(skip_path) for skip_path in skip_paths):
            return await call_next(request)
        
        # Only apply to protected routes (dashboard endpoints)
        # Apply to all /api/v1 routes except /auth and /docs endpoints
        if path.startswith("/api/v1/") and not path.startswith("/api/v1/auth"):
            client_ip = self.get_client_ip(request)
            
            # If no whitelist configured, allow all
            if not self.allowed_ips and not self.allowed_networks:
                return await call_next(request)
            
            # Check if IP is allowed
            if not self.is_allowed_ip(client_ip):
                logger.warning(f"Access denied for IP: {client_ip} to {path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "message": "Access denied",
                        "detail": f"IP address {client_ip} is not authorized to access this resource. Please contact administrator."
                    }
                )
            
            logger.debug(f"Access granted for IP: {client_ip} to {path}")
        
        return await call_next(request)

