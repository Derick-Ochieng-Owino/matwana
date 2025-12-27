import os
from pathlib import Path
from urllib.parse import urlparse
import dj_database_url
from dotenv import load_dotenv

# 1. INITIAL SETUP
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-dev-only')
DEBUG = True

# 2. HOST CONFIGURATION
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
SUPABASE_URL = os.getenv('SUPABASE_URL', '')

if SUPABASE_URL:
    parsed_url = urlparse(SUPABASE_URL)
    if parsed_url.netloc:
        ALLOWED_HOSTS.append(parsed_url.netloc)

# 3. APPLICATION DEFINITION
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'matwanaapp', # Your core app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'matwana.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'matwana.wsgi.application'

# 4. DATABASE CONFIGURATION (Supabase Optimized)
database_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')

if not database_url:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True
        )
    }
    # Supabase Connection Pooling Tweaks
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
    DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = True  # Required for Port 6543
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}

# 5. AUTHENTICATION & USER
# Note: Uncomment the line below once you fix your User model to inherit from AbstractUser
AUTH_USER_MODEL = 'matwanaapp.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 6. INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi' # Updated for your context
USE_I18N = True
USE_TZ = True

# 7. STATIC & MEDIA FILES
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 8. SECURITY (Production settings)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True