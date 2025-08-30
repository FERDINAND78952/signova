from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key-here")

DEBUG = False  # Default — will be overridden in dev

ALLOWED_HOSTS = []  # Override in prod

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "signova_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "signova.bad_request_middleware.BadRequestMiddleware",
]

# Add memory optimization middleware on Render
IS_RENDER = os.environ.get('RENDER', 'False').lower() == 'true' or os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None
if IS_RENDER:
    MIDDLEWARE.append('signova.middleware.MemoryOptimizationMiddleware')

ROOT_URLCONF = "signova.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "signova.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configure whitenoise for better performance
WHITENOISE_MAX_AGE = 31536000 # 1 year in seconds
WHITENOISE_AUTOREFRESH = False

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

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
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', '')
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', '')
    
    SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('SOCIAL_AUTH_FACEBOOK_KEY', '')
    SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('SOCIAL_AUTH_FACEBOOK_SECRET', '')
    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
    
    SOCIAL_AUTH_TWITTER_KEY = os.getenv('SOCIAL_AUTH_TWITTER_KEY', '')
    SOCIAL_AUTH_TWITTER_SECRET = os.getenv('SOCIAL_AUTH_TWITTER_SECRET', '')

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Flutterwave Configuration
FLW_SECRET_KEY = os.getenv('FLW_SECRET_KEY', 'FLWSECK_TEST-YOUR-SECRET-KEY-HERE')
FLW_PUBLIC_KEY = os.getenv('FLW_PUBLIC_KEY', 'FLWPUBK_TEST-YOUR-PUBLIC-KEY-HERE')
FLUTTERWAVE_ENABLED = os.getenv('FLUTTERWAVE_ENABLED', 'True').lower() == 'true'

# Flutterwave Django Configuration
FLW_PRODUCTION = not DEBUG  # Use test mode in development
FLW_SANDBOX = DEBUG  # Use sandbox in development
FLW_REDIRECT_URL = 'payment_callback'  # URL name for payment callback
FLW_WEBHOOK_HASH = os.getenv('FLW_WEBHOOK_HASH', '')  # Webhook hash for verification

# MTN Mobile Money Configuration
MTN_ENABLED = os.getenv('MTN_ENABLED', 'True').lower() == 'true'  # Enable MTN Mobile Money by default
MTN_API_KEY = os.getenv('MTN_API_KEY', '')  # MTN Mobile Money API Key
MTN_API_SECRET = os.getenv('MTN_API_SECRET', '')  # MTN Mobile Money API Secret
