from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.deletion import CASCADE
from django.utils import timezone
from accounts.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

class Team(models.Model):
    ShortName = models.CharField(max_length=4, primary_key=True)
    Town = models.CharField(max_length=20)
    Nickname = models.CharField(max_length=20)
    Conference = models.CharField(max_length=3, null=True, blank=True)
    Division  = models.CharField(max_length=5, null=True, blank=True)
    ConfDiv = models.CharField(max_length=9, null=True, blank=True)
    Logo = models.ImageField(default='football.png', upload_to='logos')

    def __str__(self):
        return('{} {}'.format(self.Town, self.Nickname))

    def save(self, *args, **kwargs):
        self.ConfDiv = str(self.Conference)+" "+str(self.Division)
        super(Team, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['Town', 'Nickname']
    


class Match(models.Model):
    Season = models.IntegerField(validators=[MinValueValidator(2012), MaxValueValidator(2050)])
    Week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(18)])
    GameID = models.IntegerField(primary_key=True,validators=[MinValueValidator(20120101)])
    HomeTeam = models.ForeignKey(Team, related_name='HomeTeam_Schedule_Set', on_delete=models.CASCADE)
    AwayTeam = models.ForeignKey(Team, related_name='AwayTeam_Schedule_Set', on_delete=models.CASCADE)
    DateTime = models.DateTimeField()
    FriendlyName = models.CharField(max_length=50, null=True, blank=True)
    TeamsName = models.CharField(max_length=50, null=True, blank=True)
    
    def update_preds(self):
        # Change Corresponding Prediction PredWeek values if Game is rearranged for Covid
        try:
            preds = Prediction.objects.filter(Game=self)
        except Prediction.DoesNotExist:
            pass
        else:
            for pred in preds:
                pred.PredWeek = int(str(self.Season)+str(self.Week))
                pred.save()

    def save(self, *args, **kwargs):
        self.FriendlyName = ('{} @ {}, Week {}, {}'.format(self.AwayTeam.Nickname, self.HomeTeam.Nickname, self.Week, self.Season))
        self.TeamsName = ('{} @ {}'.format(self.AwayTeam.Nickname, self.HomeTeam.Nickname))
        super(Match, self).save(*args, **kwargs)
        self.update_preds()

    def __str__(self):
        return('{} @ {}, Week {}, {}'.format(self.AwayTeam.Nickname, self.HomeTeam.Nickname, self.Week, self.Season))
    
    class Meta:
        verbose_name_plural = "Matches"
        ordering = ['DateTime', 'AwayTeam']

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
    PredSeason = models.IntegerField(blank=True, null=True)
    Joker = models.BooleanField(default=False)
    class Meta:
        unique_together = ("User", "Game"),
    
    def __str__(self):
        return('{}, {}, {}'.format(self.User, self.Game, self.Winner))
    
    def save(self, *args, **kwargs):
        self.PredWeek = int(str(self.Game.Season)+str(self.Game.Week))
        self.PredSeason = self.Game.Season

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
                # Create new Season score entry if none already exists
                if self.Points > 0:
                    if self.Banker == True:
                        addseasonscore = ScoresSeason(User=self.User, SeasonScore=self.Points, Season=self.Game.Season, SeasonBest=0, SeasonWorst=999, SeasonCorrect=1, SeasonAverage=self.Points, BankerAverage=self.Points)
                    else:
                        addseasonscore = ScoresSeason(User=self.User, SeasonScore=self.Points, Season=self.Game.Season, SeasonBest=0, SeasonWorst=999, SeasonCorrect=1, SeasonAverage=self.Points)
                else:
                    addseasonscore = ScoresSeason(User=self.User, SeasonScore=self.Points, Season=self.Game.Season, SeasonBest=0, SeasonWorst=999, SeasonCorrect=0, SeasonAverage=self.Points)                   
                addseasonscore.save()
            else:
                # If a Season score object exists, grab the record and update the below
                seasonscore = ScoresSeason.objects.get(User=self.User, Season=self.Game.Season)
                # Increment SeasonCorrect if pts scored
                if self.Points > 0:
                    seasonscore.SeasonCorrect += 1
                seasonscore.SeasonScore += self.Points
                seasonscore.save()

            ### Add Points to All Time Scores ###
            try:
                ScoresAllTime.objects.get(User=self.User)
            except ScoresAllTime.DoesNotExist:
                # create new all time score entry if none already exists
                if self.Points > 0:
                    if self.Banker == True:
                        addalltimescore = ScoresAllTime(User=self.User, AllTimeScore=self.Points, AllTimeWorst=999, AllTimeBest=1, AllTimeCorrect=1, AllTimeAverage=self.Points, AllTimeBankerAverage=self.Points)
                    else:
                        addalltimescore = ScoresAllTime(User=self.User, AllTimeScore=self.Points, AllTimeWorst=999, AllTimeBest=1, AllTimeCorrect=1, AllTimeAverage=self.Points)
                else:
                    addalltimescore = ScoresAllTime(User=self.User, AllTimeScore=self.Points, AllTimeWorst=999, AllTimeBest=1, AllTimeCorrect=0, AllTimeAverage=self.Points)
                addalltimescore.save()
            else:
                # if an all time score object exists, add the points to it
                alltimescore = ScoresAllTime.objects.get(User=self.User)
                # Increment AllTimeCorrect if pts scored
                if self.Points > 0:
                    alltimescore.AllTimeCorrect += 1
                alltimescore.AllTimeScore += self.Points
                alltimescore.save()
            super(Prediction, self).save(*args, **kwargs)

class ScoresWeek(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(18)])
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
    SeasonWorst = models.IntegerField(null=True, blank=True)#
    SeasonBest = models.IntegerField(null=True, blank=True)#
    SeasonCorrect = models.IntegerField(null=True, blank=True)#
    SeasonPercentage = models.DecimalField(max_digits=4, decimal_places=1,null=True, blank=True)#
    SeasonAverage = models.DecimalField(max_digits=5, decimal_places=1,null=True, blank=True)#
    BankerAverage = models.DecimalField(max_digits=4, decimal_places=1,null=True, blank=True)#
    Season = models.IntegerField(validators=[MinValueValidator(2012), MaxValueValidator(2050)])

    def __str__(self):
        return('{}, Season {}: {}'.format(self.User, self.Season, self.SeasonScore))

    class Meta:
        verbose_name_plural = "Season Scores"
        ordering = ['-SeasonScore', '-SeasonCorrect', '-BankerAverage', 'User']

class ScoresAllTime(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    AllTimeWorst = models.IntegerField(null=True, blank=True)#
    AllTimeBest = models.IntegerField(null=True, blank=True)#
    AllTimeCorrect = models.IntegerField(null=True, blank=True)#
    AllTimePercentage = models.DecimalField(max_digits=4, decimal_places=1,null=True, blank=True)#
    AllTimeAverage = models.DecimalField(max_digits=5, decimal_places=1,null=True, blank=True)#
    AllTimeBankerAverage = models.DecimalField(max_digits=4, decimal_places=1,null=True, blank=True)#
    AllTimeScore = models.IntegerField()

    def __str__(self):
        return('{}, All Time Score: {}'.format(self.User, self.AllTimeScore))

    class Meta:
        verbose_name_plural = "All Time Scores"
        ordering = ['-AllTimeScore', 'User']

class Results(models.Model):
    Season = models.IntegerField(validators=[MinValueValidator(2012), MaxValueValidator(2050)])
    Week = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(18)])
    GameID = models.IntegerField(primary_key=True,validators=[MinValueValidator(20100101)])
    HomeTeam = models.ForeignKey(Team, related_name='HomeTeam_Results_Set', on_delete=models.CASCADE)
    AwayTeam = models.ForeignKey(Team, related_name='AwayTeam_Results_Set', on_delete=models.CASCADE)
    HomeScore = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    AwayScore = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    Winner = models.CharField(max_length=4)

    # Below logic will iterate over corresponding predictions
    # And update the points on each prediction
    
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
                    if pred.Joker == True:
                        pred.Points = (pred.Points * 3)
                    pred.save()
                else:
                    pred.Points = 0
                    pred.save()
            # If Banker record does exist, score it
            else:
                if pred.Winner == self.Winner:
                    pred.Points = scored*2
                    if pred.Joker == True:
                        pred.Points = (pred.Points * 3)
                    pred.save()
                else:
                    pred.Points = 0-(scored*2)
                    if pred.Joker == True:
                        pred.Points = (pred.Points * 3)
                    pred.save()
        super(Results, self).save(*args, **kwargs)

    def __str__(self):
        return('{} @ {}, Week {}, {}'.format(self.AwayTeam.Nickname, self.HomeTeam.Nickname, self.Week, self.Season))
    
    class Meta:
        verbose_name_plural = "Results"

class Record(models.Model):
    Title = models.CharField(max_length=100, null=True, blank=True)
    Holders = models.ManyToManyField(User)
    Year = models.IntegerField(validators=[MinValueValidator(1990), MaxValueValidator(2100)])
    Week = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(25)], blank=True, null=True)
    Record = models.CharField(max_length=50, null=True, blank=True)
    Priority = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)])

    def __str__(self):
        return('{}: {}, in {}'.format(self.Title, self.Record, self.Year))

    class Meta:
        verbose_name_plural = "Records"
        ordering = ['Priority']

class AvgScores(models.Model):
    Season = models.IntegerField(validators=[MinValueValidator(1990), MaxValueValidator(2100)])
    AvgScores = JSONField(null=True)

    def __str__(self):
        return("Average Weekly Scores")