"""
Django settings for crm project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

# from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# config apps path
sys.path.insert(0, os.path.join(BASE_DIR, 'libs'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ao!yd&&y(2a(_i1c2x*fkj)v#3(x9l&d7uayw%$dcmw+er8ljp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # xadmin
    'xadmin',
    'crispy_forms',
    'reversion',
    #
    'celery',
    'django_celery_beat',
    #
    'rest_framework',
    'rest_framework_swagger',
    # apps
    'crm.core',
    'crm.user',
    'crm.sale',
    'crm.discount',
    'crm.report',
    'crm.restapi',
    'crm.gaoyou',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'crm.core.middleware.AccessAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crm.settings.urls'

AUTH_USER_MODEL = 'user.BackendUser'

AUTHENTICATION_BACKENDS = ('crm.core.views.CustomBackend',)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'crm.settings.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static/'

REDIS_URL = "redis://127.0.0.1:6379/0"

# Celery settings
# Broker url
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    # 'SyncAwxBaseInfo': {
    #     'task': 'jianbox.boxinfo.tasks.SyncAwxBaseInfo',
    #     'schedule': 60,
    # },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'crm.restapi.auth.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS':
    # 'rest_framework.pagination.LimitOffsetPagination',
        "crm.core.utils.CustomPagination",
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter'),
    'PAGE_SIZE': 15,
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}

LOG_DIR = os.path.join(BASE_DIR, '../logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'  # noqa
        },
    },
    'handlers': {
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,  # noqa
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
        }
    }
}
# cache session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Swagger
LOGIN_URL = '/xadmin'
LOGOUT_URL = '/xadmin'

# Coin Update
ERP_JIAN24_URL = 'http://test.jian24.com'

from .local_settings import *

UPDATE_USER_COIN = ERP_JIAN24_URL + '/update'

# signature key
INTERNAL_KEY = '8d1235sa0e212f10'
INTERNAL_SALT = 's38d'
# 超级用户： admin    admin

# # 设置sentry错误日志监控系统
# sentry_sdk.init(
#
#     # 5c5e2401017a405e90c5120a833b9a3d59fa58df50574bae87b40abcf96c2c78
#     dsn="https://e7e81725e8b3425fa67825898bf745b6@sentry.io/1529255",
#     integrations=[DjangoIntegration()]
# )
