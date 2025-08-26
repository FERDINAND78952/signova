from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

# Check if we're on Render deployment
IS_RENDER = (os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None or 
            os.environ.get('RENDER', 'False').lower() == 'true')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('signova_app.urls')),
]

# Only include social auth URLs when not on Render
if not IS_RENDER:
    urlpatterns.append(path('social-auth/', include('social_django.urls', namespace='social')))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)