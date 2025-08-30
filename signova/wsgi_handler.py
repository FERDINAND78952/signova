import logging
import traceback
import sys
from django.core.handlers.wsgi import WSGIHandler
from django.http import HttpResponse

logger = logging.getLogger('django')

class CustomWSGIHandler(WSGIHandler):
    """
    Custom WSGI handler that catches and handles Bad Request (400) errors
    that might occur at the WSGI level before reaching Django's middleware.
    """
    
    def __call__(self, environ, start_response):
        try:
            # Log request details for debugging
            path_info = environ.get('PATH_INFO', '')
            request_method = environ.get('REQUEST_METHOD', '')
            remote_addr = environ.get('REMOTE_ADDR', '')
            http_host = environ.get('HTTP_HOST', '')
            http_user_agent = environ.get('HTTP_USER_AGENT', '')
            
            logger.info(f"WSGI Processing request: {request_method} {path_info} from {remote_addr}, Host: {http_host}")
            logger.info(f"WSGI Request headers: HTTP_HOST={http_host}, HTTP_USER_AGENT={http_user_agent}")
            
            # Log all environment variables for debugging
            logger.debug("WSGI Environment Variables:")
            for key, value in sorted(environ.items()):
                logger.debug(f"  {key}: {value}")
            
            return super().__call__(environ, start_response)
        except Exception as e:
            # Log detailed exception information
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(f"WSGI Exception: {str(e)}")
            logger.error(f"Exception type: {exc_type.__name__}")
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            
            # Log request details
            path_info = environ.get('PATH_INFO', '')
            request_method = environ.get('REQUEST_METHOD', '')
            remote_addr = environ.get('REMOTE_ADDR', '')
            http_host = environ.get('HTTP_HOST', '')
            
            logger.error(f"Request details: {request_method} {path_info} from {remote_addr}, Host: {http_host}")
            
            # Create a simple error response
            status = '400 Bad Request'
            response_headers = [('Content-type', 'text/html')]
            
            # Simple HTML error page
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
            '''.encode('utf-8')
            
            start_response(status, response_headers)
            return [html_content]