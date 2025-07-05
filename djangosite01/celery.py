from djangosite01.settings import CELERY_BROKER_URL
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangosite01.settings')

# Check if we're in a local dev environment (which might not always have debug)
try:
    myenv = os.environ.get('ENVIRONMENT').lower()
except:
    myenv = 'environmentmissing'
    
IS_LOCALDEV = myenv == ('localdev')
IS_HEROKU = myenv == ('heroku')
IS_APPLIKU = myenv == ('appliku')

# Check if in Local Dev - Heroku now needs extra arg in URL
if IS_LOCALDEV:
    CELERY_BROKER_URL = os.environ['REDIS_URL']
else: 
    try:
        CELERY_BROKER_URL = os.environ['REDIS_URL']+"?ssl_cert_reqs=CERT_NONE"
    except:
        CELERY_BROKER_URL = "redis://127.0.0.1:6379"

app = Celery('djangosite01', CELERY_BROKER_URL=CELERY_BROKER_URL)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')