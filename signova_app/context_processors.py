from django.conf import settings

def installed_apps(request):
    """
    Adds the INSTALLED_APPS setting to the template context
    """
    return {'INSTALLED_APPS': settings.INSTALLED_APPS}