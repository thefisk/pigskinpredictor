from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
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
    ShortName = models.CharField(max_length=4, primary_key=True)
    Town = models.CharField(max_length=20)
    Nickname = models.CharField(max_length=20)
    
    def __str__(self):
        return('{} {}'.format(self.Town, self.Nickname))

class Results(models.Model):
    Week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(17)])
    GameID = models.IntegerField(primary_key=True,validators=[MinValueValidator(2010010101)])
    HomeTeam = models.ForeignKey(Team, related_name='HomeTeam_Results_Set', on_delete=models.CASCADE)
    AwayTeam = models.ForeignKey(Team, related_name='AwayTeam_Results_Set', on_delete=models.CASCADE)
    HomeScore = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    AwayScore = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    Winner = models.CharField(max_length=4)

    # Below save override works for manual entry
    # But manage.py loaddata ignores this as it's
    # A straight database dump
    # Logic kept but duplicated to fetchresults.py
    def save(self, *args, **kwargs):
        if self.HomeScore == self.AwayScore:
            self.Winner = 'Tie'
        elif self.HomeScore > self.AwayScore:
            self.Winner = 'Home'
        else:
            self.Winner = 'Away'
        super(Results, self).save(*args, **kwargs)

    def __str__(self):
        return('{} @ {}, week {}'.format(self.AwayTeam.Nickname, self.HomeTeam.Nickname, self.Week))
    
    class Meta:
        verbose_name_plural = "Results"