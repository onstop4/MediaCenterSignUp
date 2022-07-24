"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 3.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from datetime import time
from os import environ
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "django_filters",
    "signup.apps.SignupConfig",
    "signup.faculty.apps.FacultyConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
    "constance",
    "django_celery_beat",
    "django_celery_results",
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
]

ROOT_URLCONF = "project.urls"

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

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="postgres"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "static_collected"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "signup.User"

AUTHENTICATION_BACKENDS = [
    "signup.auth.OAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET")

# Allows OAuthlib to work when HTTPS isn't an option. See https://bit.ly/3OUWd4s for
# more info.
if config("OAUTHLIB_INSECURE_TRANSPORT", cast=bool):
    environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

LOGIN_URL = "index"

CONSTANCE_BACKEND = "project.constance.ImprovedRedisBackend"

CONSTANCE_REDIS_CONNECTION = {
    "host": config("CONSTANCE_REDIS_HOST", default="127.0.0.1"),
    "port": config("CONSTANCE_REDIS_PORT", cast=int, default=6379),
    "db": config("CONSTANCE_REDIS_DB", cast=int, default=0),
    "password": config("CONSTANCE_REDIS_PASSWORD"),
}

CONSTANCE_CONFIG = {
    # Sets the maximum number of periods in a day.
    "MAX_PERIOD_NUMBER": (
        config("DEFAULT_MAX_PERIOD_NUMBER", cast=int),
        "maximum number of periods",
    ),
    # Determines if the form should be kept open regardless of the times below.
    "FORCE_OPEN_SIGN_UP_FORM": (
        config("DEFAULT_FORCE_OPEN_SIGN_UP_FORM", cast=bool, default=False),
        "force sign-up form to be open",
    ),
    # Determines when the form opens.
    "SIGN_UP_FORM_OPENS_TIME": (
        time(*(int(i) for i in config("DEFAULT_SIGN_UP_FORM_OPENS_TIME").split(":"))),
        "time sign-up form opens",
    ),
    # Determines when the form closes.
    "SIGN_UP_FORM_CLOSES_TIME": (
        time(*(int(i) for i in config("DEFAULT_SIGN_UP_FORM_CLOSES_TIME").split(":"))),
        "time sign-up form closes",
    ),
    # Students can indicate if they are signing up because they have lunch or because
    # they have study hall between LUNCH_PERIODS_START and LUNCH_PERIODS_END. For the
    # periods before LUNCH_PERIODS_START and after LUNCH_PERIODS_END, they can only
    # indicate that they are signing up because they have study hall.
    "LUNCH_PERIODS_START": (
        config("DEFAULT_LUNCH_PERIODS_START", cast=int),
        "first lunch period",
    ),
    "LUNCH_PERIODS_END": (
        config("DEFAULT_LUNCH_PERIODS_END", cast=int),
        "last lunch period",
    ),
}

CRISPY_TEMPLATE_PACK = "bootstrap4"
CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap4", "bootstrap5")

CELERY_TIMEZONE = "America/New_York"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_POOL_LIMIT = 1
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_BACKEND_MAX_RETRIES = config(
    "CELERY_RESULT_BACKEND_MAX_RETRIES", cast=int, default=2
)

_celery_redis_host = config("CELERY_REDIS_HOST", default="127.0.0.1")
_celery_redis_port = config("CELERY_REDIS_PORT", cast=int, default=6379)
_celery_redis_db = config("CELERY_REDIS_DB", cast=int, default=1)
_celery_redis_password = config("CELERY_REDIS_PASSWORD")

CELERY_BROKER_URL = (
    f"redis://:{_celery_redis_password}@{_celery_redis_host}:"
    f"{_celery_redis_port}/{_celery_redis_db}"
)

# pylint: disable=wildcard-import, unused-wildcard-import
if not DEBUG:
    # Use settings specifically meant for production if DEBUG is False.
    from project.prod_settings import *
