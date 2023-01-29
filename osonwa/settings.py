"""
Django settings for osonwa project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!

if os.getenv("dev"):
    DEBUG = True
else:
    DEBUG = False

AUTH_USER_MODEL = "account.User"

ADMINS = [("osonwa", "osonwajohn@gmail.com")]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third party
    "corsheaders",
    "rest_framework",
    # "rest_framework_simplejwt",
    "django_quill",
    # custom apps
    "account.apps.AccountConfig",
    "blog.apps.BlogConfig",
    "news.apps.NewsConfig",
    "articles_feed.apps.ArticlesFeedConfig",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "osonwa.urls"

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

WSGI_APPLICATION = "osonwa.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD"),
        "PORT": 5432,
        "HOST": "postgresdb",
    }
}


ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "osonwa.com", "osonwa"]
CORS_ALLOW_ALL_ORIGINS = True

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST = os.getenv("HOST")
EMAIL_PORT = os.getenv("PORT")
EMAIL_HOST_USER = os.getenv("USER")
EMAIL_HOST_PASSWORD = os.getenv("PASSWORD")
EMAIL_USE_SSL = True

# Rest framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_RENDERER_CLASSES": [
        "osonwa.drf_helpers.CustomRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# SIMPLEJWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
}


# CELERY
CELERY_BROKER_URL = "redis://redisdb:6379"
CELERY_RESULT_BACKEND = "redis://redisdb:6379"
CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_ACKS_LATE = True
CELERY_CREATE_MISSING_QUEUES = True


# loggers

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "{levelname} {message}", "style": "{"},
        "standard": {
            "format": "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        },
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "simple",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "WARNING",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./logs/django.log",
            "maxBytes": (1024 * 30),
            "backupCount": 3,
        },
        "celery": {
            "level": "WARNING",
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./logs/celery.log",
            "maxBytes": (1024 * 30),
            "backupCount": 3,
        },
        "mail_admins": {
            "level": "ERROR",
            "formatter": "standard",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
        },
    },
    "loggers": {
        "celery": {
            "handlers": ["mail_admins", "celery"],
            "level": "WARNING",
            "propagate": False,
        },
        "django": {
            "handlers": ["mail_admins", "file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
