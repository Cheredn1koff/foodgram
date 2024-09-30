import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', '17tg!(#wd6k%%*+q5y%%hk&13i%(_3&pho6bw!pj_c1#3xe$5b')

DEBUG = os.getenv('DEBUG', False) == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1, localhost').split(', ')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'djoser',

    'core',
    'users',
    'recipes',
    'api',
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

ROOT_URLCONF = 'foodgram_backend.urls'


TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'foodgram_backend.wsgi.application'


POSTGRES_SETTINGS = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('POSTGRES_DB', 'django'),
    'USER': os.getenv('POSTGRES_USER', 'django'),
    'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
    'HOST': os.getenv('DB_HOST', ''),
    'PORT': os.getenv('DB_PORT', 5432)
}

SQLITE_SETTINGS = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'db.sqlite3',
}

DATABASES = {
    'default': (POSTGRES_SETTINGS, SQLITE_SETTINGS)[os.getenv('DATABASE') == 'sqlite']
}


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


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


AUTH_USER_MODEL = 'users.User'

#############################################################################
#                            Model constants
#############################################################################

STR_SYMBOLS_AMOUNT = 30

# User model


MAX_LENGTH_EMAIL = 254
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_FIRST_NAME = 150
MAX_LENGTH_LAST_NAME = 150


# Recipe model

MAX_LENGTH_RECIPE_NAME = 200
RECIPE_MIN_COOKING_TIME = 1

# Ingredient model

MAX_LENGTH_INGREDIENT_NAME = 200
INGREDIENT_MIN_AMOUNT = 1

# Unit model

MAX_LENGTH_UNIT_NAME = 200

# Tag model

MAX_LENGTH_TAG_NAME = 200
MAX_LENGTH_TAG_COLOR = 7

#############################################################################
#                            DRF settings
#############################################################################

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}


#############################################################################
#                            Djoser settings
#############################################################################


DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS':
        {
            'user': ['djoser.permissions.CurrentUserOrAdmin'],
            'user_list': ['rest_framework.permissions.AllowAny'],
        },
    'SERIALIZERS':
        {
            'user_create': 'api.serializers.UserCreateSerializer',
            'user': 'api.serializers.UserSerializer',
            'current_user': 'api.serializers.UserSerializer',
        },
}

ALLOWED_USER_ACTIONS = [
    'users-list',
    'users-me',
    'users-detail',
    'users-set-password',
    'users-subscriptions',
    'users-subscribe'
]


JSON_PATH = 'static/data/ingredients.json'
HELP_IMPORT_JSON_MESSAGE = 'Импорт данных из .json'

CSV_PATH = 'static/data/ingredients.csv'
HELP_IMPORT_CSV_MESSAGE = 'Импорт данных из .csv'


SUCCES_IMPORT_MESSAGE = 'Загрузка данных завершена'
