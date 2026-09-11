from django.core.management.base import BaseCommand
from predictor.models import Match
from datetime import datetime as dt

# Below custom managament command added in Appliku migration
# Will be called by Cron once a year to create friendly names on match entries
# in readiness for the new season

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Use datetime module to get current year
        season = dt.now().year

        matches = Match.objects.get(Season=season)
        for match in matches:
            match.save()