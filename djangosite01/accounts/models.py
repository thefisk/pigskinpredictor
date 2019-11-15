from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, PermissionsMixin



class User(AbstractUser):
    FavouriteTeam = models.ForeignKey('predictor.Team', on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return str(self.first_name +" "+self.last_name)
    
    class Meta:
        verbose_name_plural = "My Custom User Class"