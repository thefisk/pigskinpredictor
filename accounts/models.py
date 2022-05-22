from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin
from .timezones import timezonelist


class User(AbstractUser):
    FavouriteTeam = models.ForeignKey('predictor.Team', on_delete=models.CASCADE, blank=True, null=True)
    Full_Name = models.CharField(max_length=100, null=True, blank=True)
    Reminder48 = models.BooleanField(default=True, verbose_name='48 Hour Reminder Emails')
    PickConfirmation = models.BooleanField(default=False, verbose_name='Pick Confirmation Emails')
    SundayLive = models.BooleanField(default=True, verbose_name='Show Sunday Live Scores')
    # JokerUsed was in use in 2021 season - needs removing
    JokerUsed = models.IntegerField(null=True, blank=True, verbose_name='Joker Used')
    # JokersPlayed introduced in 2022 to replace above
    JokersPlayed = JSONField(null=True, blank=True)
    Positions = JSONField(null=True, blank=True)
    Timezone = models.CharField(null=True, blank=True, choices=timezonelist, default="Europe/London", max_length=50)
    
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.Full_Name = str(self.first_name +" "+self.last_name)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.first_name +" "+self.last_name)
    
    class Meta:
        verbose_name_plural = "Pigskin User Profile"