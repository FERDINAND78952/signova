import os
from django.apps import AppConfig

class SignovaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'signova_app'
    
    def ready(self):
        # Check if we're running on Render and disable TensorFlow if needed
        is_render = os.environ.get('RENDER', 'False').lower() == 'true'
        if is_render:
            # Set environment variables to optimize memory usage
            os.environ['DISABLE_TENSORFLOW'] = 'True'
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable TensorFlow logging
            
            # Prevent loading of ML models in memory
            os.environ['SIGNOVA_DISABLE_ML'] = 'True'