"""
Django settings for config project.
"""

from pathlib import Path

# Base directory of project
BASE_DIR = Path(__file__).resolve().parent.parent

from decouple import config
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)

# Empty now, later add domain/IP in production
ALLOWED_HOSTS = []


# INSTALLED APPS
INSTALLED_APPS = [
    # Default Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'returns',
    'accounts',
    'products',
    'sales',
    'inventory',
    'dashboard',
    'purchase',
]


# MIDDLEWARE = request/response processing layers
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',   # protects forms
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


# TEMPLATE SETTINGS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Global templates folder
        'DIRS': [BASE_DIR / 'templates'],

        # Also checks templates folder inside each app
        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}


# PASSWORD VALIDATION
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


# LANGUAGE + TIMEZONE
LANGUAGE_CODE = 'en-us'

# Important for Pakistan sales timings
TIME_ZONE = 'Asia/Karachi'

USE_I18N = True
USE_TZ = True


# STATIC FILES
STATIC_URL = 'static/'

# Admin customizations
ADMIN_SITE_HEADER = "Farman Electronics POS"
ADMIN_SITE_TITLE = "Farman Electronics Admin"
ADMIN_INDEX_TITLE = "Management Dashboard"

# Static files for admin
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# MEDIA FILES (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'