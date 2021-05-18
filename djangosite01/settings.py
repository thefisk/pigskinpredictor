import os, django_heroku
from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.environ.get('DEBUG_VALUE') == ('True'))

ALLOWED_HOSTS = ['pigskinpredictor.herokuapp.com','pigskin-dev.herokuapp.com','pigskinpredictor.com', 'pigskin-2021.herokuapp.com']


# Application definition

INSTALLED_APPS = [
    'debug_toolbar',
    'api',
    'blog',
    'material',
    'predictor.apps.PredictorConfig',
    'accounts.apps.AccountsConfig',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_extensions',
    'storages',
    'django_celery_beat',
    'django_inlinecss',
    'rest_framework',
    'django_filters',
    'dbbackup',
    'allauth',
    'allauth.account',
    'allauth.socialaccount'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'redirect_to_non_www.middleware.RedirectToNonWww',
]

ROOT_URLCONF = 'djangosite01.urls'

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

WSGI_APPLICATION = 'djangosite01.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('LOCALDBNAME'),
        'USER': os.environ.get('LOCALDBUSER'),
        'PASSWORD': os.environ.get('LOCALDBPASS'),
        'HOST': 'localhost',
        'PORT': '',
    }
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

LOGIN_URL= '/accounts/login'

STATIC_ROOT = os.path.join(BASE_DIR, 'predictor/static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND ='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'eu-west-2'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

STATIC_LOCATION = 'static'

if DEBUG == True:
    # Use local static files
    STATIC_URL = '/static/'
else:
# Use S3 static files
    STATIC_URL = 'https://{}.s3.{}.amazonaws.com/{}/'.format(AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME,STATIC_LOCATION)
    STATICFILES_STORAGE = 'predictor.storage_backends.StaticStorage'
    # Redirect http to https
    SECURE_SSL_REDIRECT = True

MEDIA_LOCATION = 'media'
MEDIA_URL = 'https://{}.s3.{}.amazonaws.com/media/'.format(AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME)

DEFAULT_FILE_STORAGE = 'predictor.storage_backends.MediaStorage'

# Django-dbbackup settings
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '~/djangodbbackup'}

# New Email-based user auth
AUTH_USER_MODEL = 'accounts.User'

# AllAuth email login settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 2

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = DEFAULT_FROM_EMAIL = 'thepigskinpredictor@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS=7
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_ADAPTER = "accounts.adapters.AccountAdapter"

ACCOUNT_FORMS = {
'signup': 'accounts.forms.CustomSignupForm',
}

# staticfiles=False added so Heroku will use S3.  Without, it uses local!
django_heroku.settings(locals(), staticfiles=False)

INTERNAL_IPS = ['127.0.0.1']

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' : ('rest_framework.permissions.IsAuthenticated',)
}

CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/London'
CELERY_BEAT_SCHEDULE = {
    '48hr Email Reminder': {
        'task': 'predictor.tasks.email_reminder',
        'schedule': crontab(hour=20, minute=00, day_of_week=2),
        'args': ['48']
    },
    '24hr Email Reminder': {
        'task': 'predictor.tasks.email_reminder',
        'schedule': crontab(hour=20, minute=00, day_of_week=3),
        'args': ['24']
    },
     '1hr Email Reminder': {
        'task': 'predictor.tasks.email_reminder',
        'schedule': crontab(hour=19, minute=00, day_of_week=4),
        'args': ['1']
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL')+"/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "pigskindjango",
    }
}