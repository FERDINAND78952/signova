import os
import gc
import sys

from django.core.wsgi import get_wsgi_application
from signova.wsgi_handler import CustomWSGIHandler

# Set memory optimization environment variables before loading Django
is_render = os.environ.get('RENDER', 'False').lower() == 'true' or os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None
if is_render:
    # Disable TensorFlow and ML features on Render
    os.environ['DISABLE_TENSORFLOW'] = 'True'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable TensorFlow logging
    os.environ['MALLOC_TRIM_THRESHOLD_'] = '65536'  # Memory trimming threshold
    
    # Force garbage collection to run more aggressively
    gc.set_threshold(100, 5, 5)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signova.settings')

# Get the standard WSGI application
base_application = get_wsgi_application()

# Use our custom WSGI handler on Render to catch 400 errors
if is_render:
    application = CustomWSGIHandler()
else:
    application = base_application