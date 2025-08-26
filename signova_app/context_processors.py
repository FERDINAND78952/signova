from django.conf import settings
from django.urls import get_resolver

def render_settings(request):
    """
    Adds IS_RENDER flag and URL namespaces to template context
    """
    # Get all available URL namespaces
    resolver = get_resolver()
    url_namespaces = set()
    
    # Extract namespaces from URL patterns
    for key, value in resolver.namespace_dict.items():
        if key:
            url_namespaces.add(key)
    
    return {
        'IS_RENDER': settings.IS_RENDER,
        'url_namespaces': url_namespaces
    }