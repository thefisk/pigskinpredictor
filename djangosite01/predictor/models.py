from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})

class Team(models.Model):
    ShortName = models.CharField(max_length=4)
    Town = models.CharField(max_length=20)
    Nickname = models.CharField(max_length=20)
    
    def __str__(self):
        return('{} {}'.format(self.Town, self.Nickname))