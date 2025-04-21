import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Host/domain names that are valid for this site
ALLOWED_HOSTS = [
    'fastdelivery.gtl-europe.de',
    'www.fastdelivery.gtl-europe.de',
    'fastdelivery.gti-europe.de',  # Versiunea corectă pentru dispozitive mobile
    'www.fastdelivery.gti-europe.de',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.replit.app',
    '.repl.co',
    '.replit.dev',
]

# Setări CSRF originale - acestea sunt uitate când CSRF_TRUSTED_ORIGINS este redefinit mai jos
# Nu ștergeți aceste setări!
CSRF_TRUSTED_ORIGINS = [
    'https://*.repl.co',
    'https://*.replit.dev',
    'https://*.replit.app',
    'http://localhost:5000',
    'http://0.0.0.0:5000',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'crispy_bootstrap5',
    'channels',
    
    # Local apps
    'accounts',
    'recruitment',
    'core',
    'chatbot',
    'utils',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Add locale middleware for language detection
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'utils.middleware.TranslationDebugMiddleware',  # Add Translation Debug middleware
    'utils.middleware.SessionErrorMiddleware',  # Add middleware to handle session errors
]

ROOT_URLCONF = 'driver_recruitment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utils.context_processors.translation_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'driver_recruitment.wsgi.application'
ASGI_APPLICATION = 'driver_recruitment.asgi.application'

# Channels configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # For development
    }
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600,
        ssl_require=False,
        conn_health_checks=True
    )
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'de'  # German as default language
TIME_ZONE = 'Europe/Berlin'  # German timezone
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Available languages
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
    ('ro', _('Romanian')),
    ('pl', _('Polish')),
    ('uk', _('Ukrainian')),
    ('ar', _('Arabic')),
    ('tr', _('Turkish')),
]

# Path where Django looks for translation files
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# django-allauth settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Changed from 'mandatory' to 'optional' for easier testing
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = True
# Let's disable the custom signup form for now to avoid circular imports
# ACCOUNT_SIGNUP_FORM_CLASS = 'accounts.signup_forms.CustomSignupForm'

# Instead, we'll add these fields to make sure they're required
ACCOUNT_FORMS = {
    'signup': 'allauth.account.forms.SignupForm',
}
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email configuration
# Using SendGrid for email delivery
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'fastdelivery@gti-europe.de')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Enable SMTP settings for SendGrid
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey'  # This is exactly the string 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Toggle sandbox mode (when True, emails are logged but not sent)
SENDGRID_SANDBOX_MODE_IN_DEBUG = False  # Disable sandbox mode to send real emails
# Echo to stdout when in sandbox mode and emails are not sent
SENDGRID_ECHO_TO_STDOUT = True

# Email template configuration for reset password and other emails
ACCOUNT_EMAIL_SUBJECT_PREFIX = "FastDelivery - "
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"  # Use HTTPS for links in emails
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = "optional"

# Additional allauth settings for better email functionality
ACCOUNT_CONFIRM_EMAIL_ON_GET = True  # Allow confirming email on GET request
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False  # Don't logout after password change
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True  # Log user in after they reset their password
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # Log user in after they confirm their email

# Google Sheets Integration
GOOGLE_SHEETS = {
    'enabled': os.environ.get('GOOGLE_SHEETS_ENABLED', 'False') == 'True',
    'spreadsheet_id': os.environ.get('GOOGLE_SHEETS_ID', ''),  # Add your Google Sheet ID here
}

# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

# Google Translate API Configuration
GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY', '')

# Translation settings
TRANSLATIONS_FALLBACK_TO_GOOGLE = True  # Whether to use Google Translate for missing translations
TRANSLATION_DEBUG = True  # Whether to log translation requests and responses

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    # Domeniul original gtl-europe.de
    'https://fastdelivery.gtl-europe.de',
    'http://fastdelivery.gtl-europe.de', 
    'https://fastdelivery.gtl-europe.de:*',
    'http://fastdelivery.gtl-europe.de:*',
    
    # Domeniul mobil gti-europe.de
    'https://fastdelivery.gti-europe.de',
    'http://fastdelivery.gti-europe.de', 
    'https://fastdelivery.gti-europe.de:*',
    'http://fastdelivery.gti-europe.de:*',
    
    # Domenii Replit pentru dezvoltare
    'https://*.replit.app',
    'http://*.replit.app',
    'https://*.replit.dev',
    'http://*.replit.dev',
    'https://*.picard.replit.dev',
    'http://*.picard.replit.dev',
]

# Set this to False to disable the CSRF debug page
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Securitate pentru cookies
# În mediul de dezvoltare, dezactivăm temporar unele măsuri de securitate
# În producție, acestea ar trebui reactivate
CSRF_COOKIE_SECURE = False  # În dezvoltare, permitem și HTTP
CSRF_COOKIE_HTTPONLY = True  # Nu permite accesul JavaScript la cookie
CSRF_USE_SESSIONS = False   # În dezvoltare, folosim cookie-uri pentru CSRF tokens
CSRF_COOKIE_SAMESITE = 'Lax'  # Restricționează cookie-urile cross-site

# Ajustări pentru mediul de producție
# Când site-ul este în producție, acestea ar trebui activate:
# CSRF_COOKIE_SECURE = True  # Folosit doar peste HTTPS
# CSRF_USE_SESSIONS = True  # Stochează CSRF token în sesiune în loc de cookie
