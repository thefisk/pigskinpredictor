from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

class Team(models.Model):
    ShortName = models.CharField(max_length=4, primary_key=True)
    Town = models.CharField(max_length=20)
    Nickname = models.CharField(max_length=20)
    Logo = models.ImageField(default='football.png', upload_to='logos')
    
    def __str__(self):
        return('{} {}'.format(self.Town, self.Nickname))

class Match(models.Model):
    Season = models.IntegerField(validators=[MinValueValidator(2012), MaxValueValidator(2050)])
    Week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(17)])
    GameID = models.IntegerField(primary_key=True,validators=[MinValueValidator(2010010101)])
    HomeTeam = models.ForeignKey(Team, related_name='HomeTeam_Schedule_Set', on_delete=models.CASCADE)
    AwayTeam = models.ForeignKey(Team, related_name='AwayTeam_Schedule_Set', on_delete=models.CASCADE)
    DateTime = models.DateTimeField()
    
    def __str__(self):
        return('{} @ {}, Week {}, {}'.format(self.AwayTeam.Nickname, self.HomeTeam.Nickname, self.Week, self.Season))
    
    class Meta:
        verbose_name_plural = "Matches"

class Banker(models.Model):
    UserSeasonKey = models.CharField(max_length=10, null=True, blank=True)
    BankerTeam = models.ForeignKey(Team, related_name="BankerTeam_Banker_Set",on_delete=models.CASCADE)
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    BankWeek = models.IntegerField(null=True, blank=True)
    BankSeason = models.IntegerField(null=True, blank=True)
    BankGame = models.ForeignKey(Match, related_name="Match_Banker_Set", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("UserSeasonKey","BankerTeam")

    def __str__(self):
        return('{}, Week {}, {}, {}'.format(self.User, self.BankWeek, self.BankSeason, self.BankerTeam))

    def save(self, *args, **kwargs):
        self.UserSeasonKey = str(self.User.id)+"_"+str(self.BankGame.Season)
        self.BankSeason = self.BankGame.Season
        self.BankWeek = self.BankGame.Week
        super(Banker, self).save(*args, **kwargs)

class Prediction(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Game = models.ForeignKey(Match, related_name='Match_Prediction_Set', on_delete=models.CASCADE)
    winner_choices = (('Home','Home'), ('Away','Away'))
    Winner = models.CharField(max_length=4, choices=winner_choices)
    Points = models.IntegerField(blank=True, null=True)
    Banker = models.BooleanField(default=False)
    PredWeek = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("User", "Game"),
    
    def __str__(self):
        return('{}, {}, {}'.format(self.User, self.Game, self.Winner))
    
    def save(self, *args, **kwargs):
        self.PredWeek = int(str(self.Game.Season)+str(self.Game.Week))

        # If new predicion (no points) just save
        if self.Points == None:
            super(Prediction, self).save(*args, **kwargs)   
        # Otherwise, add scored points to 3 x points tracker models
        else:
            ### Add Points to Weekly Scores ###
            try:
                ScoresWeek.objects.get(User=self.User, Week=self.Game.Week)
            except ScoresWeek.DoesNotExist:
                # create new weekly score entry if none already exists
                addweekscore = ScoresWeek(User=self.User, Week=self.Game.Week, WeekScore=self.Points, Season=self.Game.Season)
                addweekscore.save()
            else:
                # if a weekly score object exists, add the points to it
                weekscore = ScoresWeek.objects.get(User=self.User, Week=self.Game.Week)
                weekscore.WeekScore += self.Points
                weekscore.save()

            ### Add Points to Season Scores ###
            try:
                ScoresSeason.objects.get(User=self.User, Season=self.Game.Season)
            except ScoresSeason.DoesNotExist:
                # create new Season score entry if none already exists
                addseasonscore = ScoresSeason(User=self.User, SeasonScore=self.Points, Season=self.Game.Season)
                addseasonscore.save()
            else:
                # if a Season score object exists, add the points to it
                seasonscore = ScoresSeason.objects.get(User=self.User, Season=self.Game.Season)
                seasonscore.SeasonScore += self.Points
                seasonscore.save()

            ### Add Points to All Time Scores ###
            try:
                ScoresAllTime.objects.get(User=self.User)
            except ScoresAllTime.DoesNotExist:
                # create new all time score entry if none already exists
                addalltimescore = ScoresAllTime(User=self.User, AllTimeScore=self.Points)
                addalltimescore.save()
            else:
                # if an all time score object exists, add the points to it
                alltimescore = ScoresAllTime.objects.get(User=self.User)
                alltimescore.AllTimeScore += self.Points
                alltimescore.save()
            super(Prediction, self).save(*args, **kwargs)

class ScoresWeek(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(17)])
    WeekScore = models.IntegerField()
    Season = models.IntegerField(validators=[MinValueValidator(2012), MaxValueValidator(2050)])

    def __str__(self):
        return('{}, Week {}, {}: {}'.format(self.User, self.Week, self.Season, self.WeekScore))

    class Meta:
        verbose_name_plural = "Weekly Scores"
        ordering = ['-WeekScore', 'User']

class ScoresSeason(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    SeasonScore = models.IntegerField()
    Season = models.IntegerField(validators=[MinValueValidator(2012), MaxValueValidator(2050)])

    def __str__(self):
        return('{}, Season {}: {}'.format(self.User, self.Season, self.SeasonScore))

    class Meta:
        verbose_name_plural = "Season Scores"
        ordering = ['-SeasonScore', 'User']

class ScoresAllTime(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    AllTimeScore = models.IntegerField()

    def __str__(self):
        return('{}, All Time Score: {}'.format(self.User, self.AllTimeScore))

    class Meta:
        verbose_name_plural = "All Time Scores"
        ordering = ['-AllTimeScore', 'User']

class Results(models.Model):
    Season = models.IntegerField(validators=[MinValueValidator(2012), MaxValueValidator(2050)])
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
    # def save(self, *args, **kwargs):
    #    if self.HomeScore == self.AwayScore:
    #        self.Winner = 'Tie'
    #    elif self.HomeScore > self.AwayScore:
    #        self.Winner = 'Home'
    #    else:
    #        self.Winner = 'Away'
    #    super(Results, self).save(*args, **kwargs)


    # Below logic will iterate over corresponding predictions
    # And update the points on each prediction
    # TODO: Add banker logic
    
    def save(self, *args, **kwargs):
        if self.Winner == 'Home':
            scored = self.HomeScore
        elif self.Winner == 'Away':
            scored = self.AwayScore
        else:
            scored = 0

        thisgamepreds = Prediction.objects.filter(Game=self.GameID)

        for pred in thisgamepreds:
            # Look for matching banker record
            try:
                Banker.objects.get(BankGame=pred.Game, User=pred.User)
            # If no matching banker record found
            except:
                if pred.Winner == self.Winner:
                    pred.Points = scored
                    pred.save()
                else:
                    pred.Points = 0
                    pred.save()
            # If Banker record does exist, score it
            else:
                if pred.Winner == self.Winner:
                    pred.Points = scored*2
                    pred.save()
                else:
                    pred.Points = 0-(scored*2)
                    pred.save()
        super(Results, self).save(*args, **kwargs)

    def __str__(self):
        return('{} @ {}, Week {}, {}'.format(self.AwayTeam.Nickname, self.HomeTeam.Nickname, self.Week, self.Season))
    
    class Meta:
        verbose_name_plural = "Results"