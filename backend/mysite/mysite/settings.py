"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import hashlib
import MySQLdb
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '19!-+#%0jld%4#ygya5%t@aqaak0-^j@cz_1sh9*5=1k%dn=tp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['thuvplus.iterator-traits.com','62.234.31.126','localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'werkzeug_debugger_runserver',
    'django_extensions',
    "mysite",
    "showactivity"
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

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

WSGI_APPLICATION = 'mysite.wsgi.application'

CSRF_TRUSTED_ORIGINS = ["servicewechat.com"]


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'THUVPlus',
        'USER': 'root',
        'PASSWORD': '123',
        'HOST': '127.0.0.1',  # mysql服务所在的主机ip
        'PORT': '3306',  # mysql服务端口
        'OPTIONS': {
            'init_command': 'ALTER DATABASE THUVPlus CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci'
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
#STATICFILES_DIRS = [
 #   os.path.join(BASE_DIR, "static"),
#]
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname('__file__')))
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/media')

WX_APPID = "wx993c16f900513f44"
WX_SECRET = "fa62f60d29b4760f7a1b08a505cf9f1d"

APPID = "A13"
APPIDMD5 = hashlib.md5(APPID.encode('utf-8')).hexdigest()
TICKET_AUTHENTICATION_PREFIX = 'https://alumni-test.iterator-traits.com/fake-id-tsinghua/'
TICKET_AUTHENTICATION_MID = 'thuser/authapi/checkticket/{}/'.format(APPID)
TICKET_AUTHENTICATION = TICKET_AUTHENTICATION_PREFIX + TICKET_AUTHENTICATION_MID

WX_TOKEN_HEADER = "wx_token"
WX_OPENID_HEADER = "OPENID"
WX_CODE_HEADER = "wx_code"
WX_HTTP_API = "https://api.weixin.qq.com/sns/jscode2session"

REDIRECT_TO_LOGIN = "https://alumni-test.iterator-traits.com/fake-id-tsinghua/do/off/ui/auth/login/form/"+APPIDMD5+"/0?/login.do"

