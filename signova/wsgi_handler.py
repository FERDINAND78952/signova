import logging
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
            return super().__call__(environ, start_response)
        except Exception as e:
            # Log the exception
            logger.error(f"WSGI Exception: {str(e)}")
            
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