# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

ALLOWED_HOSTS = ['*']

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'crm',
        'USER': 'root',
        'PASSWORD': 'sui123',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8',
        },
    },
}

ERP_JIAN24_URL = 'http://test.jian24.com'
