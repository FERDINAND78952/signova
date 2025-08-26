# Signova App Package Initialization
import os

# Check if we're running on Render and disable TensorFlow if needed
is_render = os.environ.get('RENDER', 'False').lower() == 'true'
if is_render:
    os.environ['DISABLE_TENSORFLOW'] = 'True'
    # Limit memory usage for web deployment
    os.environ['MALLOC_TRIM_THRESHOLD_'] = '65536'