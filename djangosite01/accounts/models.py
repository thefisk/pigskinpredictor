from django.db import models
from django.contrib.auth.models import AbstractUser
from predictor.models import Team

class User(AbstractUser):
    FavouriteTeam = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.email