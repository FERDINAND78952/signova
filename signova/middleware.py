import gc
import os
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware:
    """Middleware to add security headers to all responses.
    
    This middleware adds various security headers to protect against common web vulnerabilities:
    - HTTP Strict Transport Security (HSTS): Forces HTTPS connections
    - Content Security Policy (CSP): Restricts resource loading to prevent XSS
    - Referrer Policy: Controls information in the Referer header
    - X-Content-Type-Options: Prevents MIME type sniffing
    - Permissions Policy: Controls access to browser features
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # HTTP Strict Transport Security (HSTS)
        # Forces browsers to use HTTPS for future requests
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy (CSP)
        # Restricts resource loading to prevent XSS attacks
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' https://cdnjs.cloudflare.com",
            "style-src 'self' https://fonts.googleapis.com https://cdnjs.cloudflare.com 'unsafe-inline'",
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com",
            "img-src 'self' data:",
            "connect-src 'self'",
            "media-src 'self'",
            "object-src 'none'",
            "frame-src 'self'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response['Content-Security-Policy'] = "; ".join(csp_directives)
        
        # Referrer Policy
        # Controls information sent in the Referer header
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # X-Content-Type-Options
        # Prevents MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Permissions Policy
        # Controls access to browser features
        permissions = [
            "camera=(self)",  # Only allow camera access on same origin
            "microphone=(self)",  # Only allow microphone access on same origin
            "geolocation=()",  # Disable geolocation
            "interest-cohort=()"  # Disable FLoC (Federated Learning of Cohorts)
        ]
        response['Permissions-Policy'] = ", ".join(permissions)
        
        # X-Frame-Options
        # Prevents clickjacking by restricting framing
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        return response


class MemoryOptimizationMiddleware:
    """Middleware to optimize memory usage on Render deployment.
    
    This middleware performs garbage collection after each request to help
    prevent memory leaks and reduce memory usage on Render's free tier.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Check both RENDER and RENDER_EXTERNAL_HOSTNAME environment variables
        self.is_render = (os.environ.get('RENDER', 'False').lower() == 'true' or 
                         os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None)
        self.request_count = 0
        self.last_full_gc = time.time()
        
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Only apply optimizations on Render
        if self.is_render:
            self.request_count += 1
            
            # Run garbage collection after every request
            collected = gc.collect(0)  # Collect generation 0 (youngest objects)
            
            # Run full garbage collection periodically
            current_time = time.time()
            if self.request_count % 10 == 0 or (current_time - self.last_full_gc) > 60:
                # Full collection of all generations
                collected += gc.collect()
                self.last_full_gc = current_time
                
                # Log memory optimization for debugging
                logger.debug(f"Full GC collected {collected} objects after {self.request_count} requests")
        
        return response