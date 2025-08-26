import gc
import os
import time
import logging

logger = logging.getLogger(__name__)

class MemoryOptimizationMiddleware:
    """Middleware to optimize memory usage on Render deployment.
    
    This middleware performs garbage collection after each request to help
    prevent memory leaks and reduce memory usage on Render's free tier.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_render = os.environ.get('RENDER', 'False').lower() == 'true'
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