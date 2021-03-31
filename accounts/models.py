from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin



class User(AbstractUser):
    FavouriteTeam = models.ForeignKey('predictor.Team', on_delete=models.CASCADE, blank=True, null=True)
    Full_Name = models.CharField(max_length=100, null=True, blank=True)
    Reminder48 = models.BooleanField(default=True, verbose_name='48 Hour Reminder Emails')
    PickConfirmation = models.BooleanField(default=False, verbose_name='Pick Confirmation Emails')
    
    def save(self, *args, **kwargs):
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        self.Full_Name = str(self.first_name +" "+self.last_name)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.first_name +" "+self.last_name)
    
    class Meta:
        verbose_name_plural = "Pigskin User Profile"