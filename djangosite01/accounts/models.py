from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    FavouriteTeam = models.ForeignKey('predictor.Team', on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.email