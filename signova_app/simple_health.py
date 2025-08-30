from django.http import HttpResponse
import logging

logger = logging.getLogger('django')

def simple_health_check(request):
    """
    A very simple health check endpoint that just returns 'OK'
    without any database connections or complex logic.
    """
    try:
        # Log request details
        logger.info(f"Simple health check accessed from {request.META.get('REMOTE_ADDR')}")
        
        # Return a simple OK response
        return HttpResponse("OK", content_type="text/plain")
    except Exception as e:
        logger.error(f"Simple health check error: {str(e)}")
        return HttpResponse(f"ERROR: {str(e)}", content_type="text/plain", status=500)