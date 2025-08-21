from django.core.management.base import BaseCommand
from accounts.models import User

# Below custom managament command added in Appliku migration
# Will be called by Cron once a year to clear down Jokers
# in readiness for the new season

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        allusers = User.objects.all()
        for user in allusers:
            user.JokersPlayed = None
            user.save()