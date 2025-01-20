import os, sentry_sdk, environ
from celery.schedules import crontab
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="change_me")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Check if we're in a local dev environment (which might not always have debug)
IS_LOCALDEV = (os.environ.get('ENVIRONMENT').lower() == ('localdev'))
IS_HEROKU = (os.environ.get('ENVIRONMENT').lower() == ('heroku'))
IS_APPLIKU = (os.environ.get('ENVIRONMENT').lower() == ('appliku'))

# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    'debug_toolbar',
    'api',
    'blog',
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
    'allauth.socialaccount',
    'viewflow',
    'viewflow.workflow'
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'redirect_to_non_www.middleware.RedirectToNonWww',
    "allauth.account.middleware.AccountMiddleware",
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

INITIAL_DB = env.db(default="sqlite:///db.sqlite3")

# if DEBUG:
#     DATABASE = INITIAL_DB | { 'OPTIONS': {
#         'sslmode' : 'allow'
#         }
#     }
# else:
#     DATABASE = INITIAL_DB

DATABASES = {
    "default": env.db(default="sqlite:///db.sqlite3")
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "default",
#         "USER": "postgres",
#         "PASSWORD": "PG_password",
#         "HOST": "pigskinpredictor-database-1234567",
#         "PORT": "5432",
#         "OPTIONS": {"sslmode": "allow"}
#     }
# }

# if DEBUG:
    # env.db seems to disregard query param and set sslmode to required, even in debug mode
    # this tweak should allow local environment to connect to PostGres without SSL
# DATABASES["default"]["OPTIONS"]["sslmode"] = "allow"

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

# Static Root is the path where static files are stored after deployment
# and is where collected static files are placed by collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, '/static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 2

# Amazon SES Settings
DEFAULT_FROM_EMAIL = "'Pigskin Predictor' <hello@pigskinpredictor.com>"
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'eu-west-2'
AWS_SES_REGION_ENDPOINT = 'email.eu-west-2.amazonaws.com'

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
# django_heroku.settings(locals(), staticfiles=False, databases=False)

INTERNAL_IPS = ['127.0.0.1']

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' : ('rest_framework.permissions.IsAuthenticated',)
}

# Check if in Local Dev - Heroku now needs extra arg in URL
if IS_LOCALDEV:
    CELERY_BROKER_URL = os.environ['REDIS_URL']
else: 
    try:
        CELERY_BROKER_URL = os.environ['REDIS_URL']+"?ssl_cert_reqs=CERT_NONE"
    except:
        CELERY_BROKER_URL = "redis://127.0.0.1:6379"

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/London'
CELERY_BEAT_SCHEDULE = {
    '48hr Email Reminder': {
        'task': 'predictor.tasks.email_reminder',
        'schedule': crontab(hour=21, minute=00, day_of_week=2),
        'args': ['48']
    },
    '24hr Email Reminder': {
        'task': 'predictor.tasks.email_reminder',
        'schedule': crontab(hour=21, minute=00, day_of_week=3),
        'args': ['24']
    },
     '1hr Email Reminder': {
        'task': 'predictor.tasks.email_reminder',
        'schedule': crontab(hour=20, minute=00, day_of_week=4),
        'args': ['1']
    },
    'Fetch and Save Results': {
        'task': 'predictor.tasks.fetch_results',
        'schedule': crontab(hour=6, minute=00, day_of_week=3),
        'args': ['0']
    },
    'Reset Jokers': {
        'task': 'predictor.tasks.joker_reset',
        'schedule': crontab(0, 0, day_of_month=1, month_of_year=4),
    },
    'Populate Live Games List': {
        'task': 'predictor.tasks.populate_live',
        'schedule': crontab(hour=12, minute=00, day_of_week=6),
    },
    'Get Live Scores (Sun)': {
        'task': 'predictor.tasks.get_livescores',
        'schedule': crontab(minute='*/1', hour='18-23', day_of_week=0),
    },
    'Get Live Scores (Mon AM)': {
        'task': 'predictor.tasks.get_livescores',
        'schedule': crontab(minute='*/1', hour='00-01', day_of_week=1),
    },
    'KickOff Time Checker': {
        'task': 'predictor.tasks.kickoff_time_checker',
        'schedule': crontab(minute=00, hour=18, day_of_week=3),
    },
    'KickOff Time Checker - Current Week - Never Runs': {
        'task': 'predictor.tasks.kickoff_time_checker_current_week',
        # 12:00 on Monday 29th Feb - i.e. a date that won't occur until 2044
        'schedule': crontab(minute=00, hour=12, day_of_week=1, day_of_month=29, month_of_year=2,),
    },
    'Save Results (No Fetch)': {
        'task': 'predictor.tasks.save_results',
        # 12:00 on Monday 29th Feb - i.e. a date that won't occur until 2044
        'schedule': crontab(minute=00, hour=12, day_of_week=1, day_of_month=29, month_of_year=2,),
    }
}

# This setting is used by Django-Redis
if IS_LOCALDEV:
    CONNECTION_POOL_KWARGS = {}
else:
    CONNECTION_POOL_KWARGS = {"ssl_cert_reqs": None}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL')+"/1",
        "OPTIONS": {
            "CONNECTION_POOL_KWARGS": CONNECTION_POOL_KWARGS,
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "pigskindjango",
    }
}


# Only initialise Sentry if Env Var present - omitted for local testing
try:
    SentryPresent = os.environ['SENTRY_DSN']
except KeyError:
    SentryAbsent = True
    
if SentryAbsent == False:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration()]
    )

# Setting Required for Models from Django 3.2 onwards
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"": {"handlers": ["console"], "level": "DEBUG"}},
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")