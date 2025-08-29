import time
from functools import wraps
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

# Define rate limits for different endpoint types
API_RATE = getattr(settings, 'API_RATE_LIMIT', '30/m')
CAMERA_RATE = getattr(settings, 'CAMERA_RATE_LIMIT', '10/m')
SPEECH_RATE = getattr(settings, 'SPEECH_RATE_LIMIT', '20/m')


def api_rate_limit(view_func):
    """
    Decorator for API endpoints that applies rate limiting based on IP address.
    Returns a 429 Too Many Requests response when rate limit is exceeded.
    """
    @wraps(view_func)
    @ratelimit(key='ip', rate=API_RATE, method=['POST', 'GET'], block=False)
    def wrapped_view(request, *args, **kwargs):
        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return JsonResponse({
                'status': 'error',
                'message': 'Rate limit exceeded. Please try again later.',
                'retry_after': '60 seconds'
            }, status=429)
        return view_func(request, *args, **kwargs)
    return wrapped_view


def camera_rate_limit(view_func):
    """
    Decorator for camera-related endpoints that applies stricter rate limiting.
    """
    @wraps(view_func)
    @ratelimit(key='ip', rate=CAMERA_RATE, method=['POST'], block=False)
    def wrapped_view(request, *args, **kwargs):
        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return JsonResponse({
                'status': 'error',
                'message': 'Camera access rate limit exceeded. Please try again later.',
                'retry_after': '60 seconds'
            }, status=429)
        return view_func(request, *args, **kwargs)
    return wrapped_view


def speech_rate_limit(view_func):
    """
    Decorator for speech-related endpoints that applies rate limiting.
    """
    @wraps(view_func)
    @ratelimit(key='ip', rate=SPEECH_RATE, method=['POST'], block=False)
    def wrapped_view(request, *args, **kwargs):
        was_limited = getattr(request, 'limited', False)
        if was_limited:
            return JsonResponse({
                'status': 'error',
                'message': 'Speech synthesis rate limit exceeded. Please try again later.',
                'retry_after': '60 seconds'
            }, status=429)
        return view_func(request, *args, **kwargs)
    return wrapped_view


class RateLimitMiddleware:
    """
    Middleware to handle rate limiting exceptions and return appropriate responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return JsonResponse({
                'status': 'error',
                'message': 'Rate limit exceeded. Please try again later.',
                'retry_after': '60 seconds'
            }, status=429)
        return None