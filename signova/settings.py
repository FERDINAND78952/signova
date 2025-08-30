# This file is a fallback for the modular settings structure
# It imports all settings from base.py and then overrides with environment-specific settings

# Import all settings from base.py
from signova.settings.base import *

# Import environment-specific settings
import os
from decouple import config
import dj_database_url  # For PostgreSQL on Render

# Override settings for this specific environment
# These settings will take precedence over the base settings

# Security key (use env variable in production)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-here')

# Debug mode - set to False in production
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "signova.onrender.com"]

# Render hostname
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    ALLOWED_HOSTS.append(".render.com")

# Only include social_django when not on Render
if not IS_RENDER and 'social_django' not in INSTALLED_APPS:
    INSTALLED_APPS.append('social_django')

# Only include social auth middleware when not on Render
if not IS_RENDER and 'social_django.middleware.SocialAuthExceptionMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.append('social_django.middleware.SocialAuthExceptionMiddleware')

# Add custom context processor
for template in TEMPLATES:
    if 'signova_app.context_processors.installed_apps' not in template['OPTIONS']['context_processors']:
        template['OPTIONS']['context_processors'].append('signova_app.context_processors.installed_apps')

# Add social_django context processors only when not on Render
if not IS_RENDER:
    for template in TEMPLATES:
        if 'social_django.context_processors.backends' not in template['OPTIONS']['context_processors']:
            template['OPTIONS']['context_processors'].append('social_django.context_processors.backends')
        if 'social_django.context_processors.login_redirect' not in template['OPTIONS']['context_processors']:
            template['OPTIONS']['context_processors'].append('social_django.context_processors.login_redirect')

# Database configuration
if config('DATABASE_URL', default=None):  # Production (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }

# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')