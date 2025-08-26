from django.conf import settings

def render_settings(request):
    """
    Adds IS_RENDER flag to template context
    """
    return {
        'IS_RENDER': settings.IS_RENDER
    }