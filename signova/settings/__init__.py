# Make settings directory a proper package
# This file allows the settings directory to be imported as a module

# Import all settings from base.py by default
from .base import *

# Import environment-specific settings based on DJANGO_SETTINGS_MODULE
import os

# Check if we're in development mode
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'signova.settings.dev':
    from .dev import *

# Check if we're in production mode
elif os.environ.get('DJANGO_SETTINGS_MODULE') == 'signova.settings.prod':
    from .prod import *