from django.core.management.base import BaseCommand
from predictor.cacheflushlist import cachestoflush
from django.core.cache import cache

# Below custom managament command added in Appliku migration
# Moved from ./predictor/apps.py because we need to run this
# AFTER the app has started in Appliku - this is triggered
# byy release.sh

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        help = "Clears caches in Redis"
        for c in cachestoflush:
            cache.delete(c)
        print('Caches flushed')