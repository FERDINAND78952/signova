import os
from pathlib import Path
from decouple import config
import dj_database_url  # For PostgreSQL on Render

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

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

# Application definition
# Check if we're on Render deployment
IS_RENDER = config('RENDER', default=False, cast=bool) or os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None

# Base installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'signova_app',
    'axes',  # Django-Axes for login protection
    'flutterwavedjango',  # Flutterwave Django integration
]

# Only include social_django when not on Render
if not IS_RENDER:
    INSTALLED_APPS.append('social_django')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'signova.middleware.SecurityHeadersMiddleware',
    'axes.middleware.AxesMiddleware',  # Django-Axes for login protection
    'django_ratelimit.middleware.RatelimitMiddleware',  # Django-Ratelimit middleware
    'signova.ratelimit_middleware.RateLimitMiddleware',  # Custom rate limit response handling
]

# Only include social auth middleware when not on Render
if not IS_RENDER:
    MIDDLEWARE.append('social_django.middleware.SocialAuthExceptionMiddleware')

# Add memory optimization middleware on Render
# Check both RENDER config and RENDER_EXTERNAL_HOSTNAME environment variable
if config('RENDER', default=False, cast=bool) or os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None:
    MIDDLEWARE.append('signova.middleware.MemoryOptimizationMiddleware')

ROOT_URLCONF = 'signova.urls'

# Define base context processors
base_context_processors = [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
]

# Add social_django context processors only when not on Render
if not IS_RENDER:
    base_context_processors.extend([
        'social_django.context_processors.backends',
        'social_django.context_processors.login_redirect',
    ])

# Define base context processors
base_context_processors = [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
]

# Add social_django context processors only when not on Render
if not IS_RENDER:
    base_context_processors.extend([
        'social_django.context_processors.backends',
        'social_django.context_processors.login_redirect',
    ])

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': base_context_processors,
        },
    },
]

WSGI_APPLICATION = 'signova.wsgi.application'

# Database configuration
if config('DATABASE_URL', default=None):  # Production (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:  # Local (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configure whitenoise for better performance
WHITENOISE_MAX_AGE = 31536000 # 1 year in seconds
WHITENOISE_AUTOREFRESH = False

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

# Django-Axes Configuration (Login Rate Limiting)
AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend should be the first backend
    'axes.backends.AxesStandaloneBackend',
    # Django's default ModelBackend
    'django.contrib.auth.backends.ModelBackend',
]

# Django-Axes Settings
AXES_FAILURE_LIMIT = 5  # Number of login attempts allowed before lockout
AXES_LOCKOUT_TIMEOUT = 30  # Lockout time in minutes
AXES_COOLOFF_TIME = 30  # Time in minutes before lockout is reset
AXES_RESET_ON_SUCCESS = True  # Reset failed attempts on successful login
AXES_LOCKOUT_TEMPLATE = None  # Use the default 403 template
AXES_LOCKOUT_URL = None  # No custom lockout URL
AXES_USE_USER_AGENT = True  # Include user agent in lockout criteria
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True  # Lock out based on both username and IP

# Django-Ratelimit Settings
RATELIMIT_VIEW = 'signova_app.views.ratelimit_view'  # View to use when rate limit is exceeded
RATELIMIT_USE_CACHE = 'default'  # Cache to use for rate limiting
RATELIMIT_ENABLE = True  # Enable rate limiting

# Custom Rate Limit Settings
API_RATE_LIMIT = '30/m'  # 30 requests per minute for general API endpoints
CAMERA_RATE_LIMIT = '10/m'  # 10 requests per minute for camera endpoints
SPEECH_RATE_LIMIT = '20/m'  # 20 requests per minute for speech endpoints

# Social Authentication - conditionally configure based on environment
if IS_RENDER:
    # On Render, only use the default Django authentication
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )
    # No need to define social auth keys on Render
else:
    # In development/other environments, include social authentication
    AUTHENTICATION_BACKENDS = (
        'social_core.backends.google.GoogleOAuth2',
        'social_core.backends.facebook.FacebookOAuth2',
        'social_core.backends.twitter.TwitterOAuth',
        'django.contrib.auth.backends.ModelBackend',
    )
    
    # Social auth keys only needed when not on Render
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', default='')
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', default='')
    
    SOCIAL_AUTH_FACEBOOK_KEY = config('SOCIAL_AUTH_FACEBOOK_KEY', default='')
    SOCIAL_AUTH_FACEBOOK_SECRET = config('SOCIAL_AUTH_FACEBOOK_SECRET', default='')
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
    
    SOCIAL_AUTH_TWITTER_KEY = config('SOCIAL_AUTH_TWITTER_KEY', default='')
    SOCIAL_AUTH_TWITTER_SECRET = config('SOCIAL_AUTH_TWITTER_SECRET', default='')

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookie security settings
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'
    
    # CSRF settings
    CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'
    CSRF_TRUSTED_ORIGINS = ['https://signova.onrender.com']
    
    # Additional security settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

# Memory optimization settings for Render
if IS_RENDER:
    # Disable TensorFlow and ML features on Render to prevent memory issues
    os.environ['DISABLE_TENSORFLOW'] = 'True'
    os.environ['SIGNOVA_DISABLE_ML'] = 'True'
    
    # Set memory optimization environment variables
    os.environ['MALLOC_TRIM_THRESHOLD_'] = '65536'  # Memory trimming threshold
    
    # Reduce Django's memory footprint
    DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
    
    # Memory trimming thresholds
    MALLOC_TRIM_THRESHOLD_ = 65536  # 64KB

# Flutterwave Configuration
FLW_PUBLIC_KEY = config('FLW_PUBLIC_KEY', default='FLWPUBK_TEST-your-public-key-here')
FLW_SECRET_KEY = config('FLW_SECRET_KEY', default='FLWSECK_TEST-your-secret-key-here')
FLW_ENCRYPTION_KEY = config('FLW_ENCRYPTION_KEY', default='your-encryption-key-here')
FLW_WEBHOOK_HASH = config('FLW_WEBHOOK_HASH', default='your-webhook-hash-here')

# Flutterwave Django Settings
FLUTTERWAVE_SECRET_KEY = FLW_SECRET_KEY
FLUTTERWAVE_PUBLIC_KEY = FLW_PUBLIC_KEY
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
