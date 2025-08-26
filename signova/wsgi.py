import os
import gc

# Set memory optimization environment variables before loading Django
is_render = os.environ.get('RENDER', 'False').lower() == 'true'
if is_render:
    # Disable TensorFlow and ML features on Render
    os.environ['DISABLE_TENSORFLOW'] = 'True'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable TensorFlow logging
    os.environ['MALLOC_TRIM_THRESHOLD_'] = '65536'  # Memory trimming threshold
    
    # Force garbage collection to run more aggressively
    gc.set_threshold(100, 5, 5)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'signova.settings')

application = get_wsgi_application()