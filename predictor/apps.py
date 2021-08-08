from django.apps import AppConfig
from .cacheflushlist import cachestoflush
from django.core.cache import cache

class PredictorConfig(AppConfig):
    name = 'predictor'
    def ready(self):
        # Caches will clear when process restarts
        # Restarts occur whenever env vars are updated on Heroku
        for c in cachestoflush:
            cache.delete(c)
        print('Caches flushed')