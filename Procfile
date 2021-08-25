web: gunicorn djangosite01.wsgi
worker: celery -A djangosite01 worker --beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler