"""
Django settings for gaschek_server project.
Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from firebase_admin import initialize_app
from dotenv import load_dotenv
import os
from pathlib import Path

# import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv("SERVER_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = [
    "localhost",
    "172.20.10.3",
    "strangely-cheerful-lion.ngrok-free.app",
    "172.20.10.3",
    "192.168.18.11",
]

# Application definition
INSTALLED_APPS = [
    "daphne",
    "channels",
    "fcm_django",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "gaschek_server",
    "device",
    "mqtt",
    "client_admin",
    "accounts",
    "orders",
    "payment",
    "notification",
]

# firebase
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    BASE_DIR, "google-credentials.json"
)
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT"),
FIREBASE_APP = initialize_app()
FCM_DJANGO_SETTINGS = {
    # an instance of firebase_admin.App to be used as default for all fcm-django requests
    # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": None,
    # default: _('FCM Django')
    "APP_VERBOSE_NAME": "FCM PUSH NOTIFICATION",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": True,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": True,
}

MIDDLEWARE = [
    "gaschek_server.middlewares.ServerNameMiddleware.ServerNameMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # 'django.middleware.gzip.GZipMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "gaschek_server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

ASGI_APPLICATION = "gaschek_server.asgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        # 'NAME': os.getenv('DATABASE_NAME'),
        "NAME": "gaschekdb",
        "USER": "postgres",
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "HOST": "localhost",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 22,
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://192.168.18.11:3000",
    # 'https://gaschek.netlify.app',
    # 'https://gaschekadmin.netlify.app',
]

CORS_ALLOW_CREDENTIALS = True

PAYSTACK_SAFE_IPS = [
    # Paystack
    "52.31.139.75",
    "52.49.173.169",
    "52.214.14.220",
]
CORS_ORIGIN_WHITELIST = ["https://gaschek.netlify.app", "http://localhost:3000"]
CSRF_TRUSTED_ORIGINS = ["https://gaschek.herokuapp.com", "http://localhost:8000"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = False
EMAIL_PORT = 465
EMAIL_HOST_USER = "gaschektechnology@gmail.com"
EMAIL_HOST_PASSWORD = "wpjzmukkuxrrgmcn"
EMAIL_USE_SSL = True


STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
