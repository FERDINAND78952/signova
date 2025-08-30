from django.http import JsonResponse, HttpResponse
from django.core.exceptions import SuspiciousOperation, DisallowedHost
import logging
import os

logger = logging.getLogger('django')

class BadRequestMiddleware:
    """
    Middleware to handle HTTP 400 Bad Request errors.
    
    This middleware catches 400 Bad Request errors that might occur when clients
    send malformed requests to the application, especially when deployed on Render.
    It also handles SuspiciousOperation and DisallowedHost exceptions.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_render = (os.environ.get('RENDER', 'False').lower() == 'true' or 
                         os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None)
        
    def __call__(self, request):
        try:
            return self.get_response(request)
        except (SuspiciousOperation, DisallowedHost) as e:
            logger.error(f"Bad Request Exception: {str(e)}")
            return self.handle_bad_request(request, e)
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 400:
                logger.error(f"Bad Request (400): {str(e)}")
                return self.handle_bad_request(request, e)
            raise
    
    def process_exception(self, request, exception):
        # Handle SuspiciousOperation exceptions (which often result in 400 errors)
        if isinstance(exception, SuspiciousOperation) or isinstance(exception, DisallowedHost):
            logger.error(f"Bad Request Exception in process_exception: {str(exception)}")
            return self.handle_bad_request(request, exception)
            
        # Check if the exception is related to bad requests
        if hasattr(exception, 'status_code') and exception.status_code == 400:
            logger.error(f"Bad Request (400) in process_exception: {str(exception)}")
            return self.handle_bad_request(request, exception)
        
        # For other exceptions, let Django handle them
        return None
    
    def handle_bad_request(self, request, exception):
        # Check if the request accepts JSON
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return JsonResponse({
                'status': 'error',
                'message': 'Bad Request: The server could not process your request.',
                'details': str(exception)
            }, status=400)
        else:
            # Return a simple HTML response for browser requests
            html_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Bad Request</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
                    h1 {{ color: #d9534f; }}
                    .container {{ border: 1px solid #eee; padding: 20px; border-radius: 5px; }}
                    .back-link {{ margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>400 Bad Request</h1>
                    <p>The server could not process your request due to invalid syntax or parameters.</p>
                    <p>Please check your request and try again.</p>
                    <div class="back-link">
                        <a href="/">Return to Homepage</a>
                    </div>
                </div>
            </body>
            </html>
            '''
            return HttpResponse(html_content, content_type='text/html', status=400)