### Script to read saved results json file
### and store in backend database in Results table
### This version is called daily by Heroku
### but will only execute on a Tuesday

import os, json, boto3, datetime
from predictor.models import Team, Results, ScoresSeason, ScoresAllTime, ScoresWeek, Prediction
from django.core.cache import cache
from .cacheflushlist import cachestoflush

def run():
   # Loop to ensure script only executes on a Thursday!
   if datetime.datetime.today().isoweekday() == 4:
      resultsweek = os.environ['RESULTSWEEK']
      if int(resultsweek) < 10:
         fileweek = '0'+resultsweek
      else:
         fileweek = resultsweek
      fileseason = os.environ['PREDICTSEASON']
      filename = 'data/resultsimport_'+fileseason+'_'+fileweek+'.json'
      bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')

      s3 = boto3.resource('s3')
      obj = s3.Object(bucket,filename)
      body = obj.get()['Body'].read().decode('utf-8')
      data = json.loads(body)

      for result in data:
         dataHome = result.get('fields').get('HomeTeam')
         dataAway = result.get('fields').get('AwayTeam')
         dataWinner = result.get('fields').get('Winner')
         dataHomeScore = result.get('fields').get('HomeScore')
         dataAwayScore = result.get('fields').get('AwayScore')
         dataGameID = result.get('pk')
         actualHome = Team.objects.get(ShortName=dataHome)
         actualAway = Team.objects.get(ShortName=dataAway)
         newresult = Results(Season=fileseason,Week=fileweek,GameID=dataGameID,HomeTeam=actualHome,AwayTeam=actualAway,HomeScore=dataHomeScore,AwayScore=dataAwayScore, Winner=dataWinner)
         newresult.save()
      
      # Update Season extended stats 
      for score in ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']):
         # Try / Except needed if a user misses a week
         try:
            weekscore = ScoresWeek.objects.get(Season=os.environ['PREDICTSEASON'], User=score.User, Week=os.environ['RESULTSWEEK'])
         except ScoresWeek.DoesNotExist:
            pass
         else:
            # Update WorstWeek if needed
            if weekscore.WeekScore < score.SeasonWorst:
               score.SeasonWorst = weekscore.WeekScore
            # Update BestWeek if needed
            if weekscore.WeekScore > score.SeasonBest:
               score.SeasonBest = weekscore.WeekScore
            # Recalculate Season Percentage
            seasoncorrect = Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User, Points__gt=0).count()
            seasonpredcount = Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User).exclude(Points__isnull=True).count()
            score.SeasonPercentage = (seasoncorrect/seasonpredcount)*100
            # Recalculate Season Average
            score.SeasonAverage = score.SeasonScore/ScoresWeek.objects.filter(Season=os.environ['PREDICTSEASON'], User=score.User).count()
            # Recalculate Banker Average
            banktotal = 0
            for banker in Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User, Banker=True):
               if isinstance(banker.Points, int):
                  banktotal += banker.Points
            score.BankerAverage=banktotal/Prediction.objects.filter(PredSeason=os.environ['PREDICTSEASON'], User=score.User, Banker=True).exclude(Points__isnull=True).count()
            score.save()

      # Update AllTime extended stats 
      for alltime in ScoresAllTime.objects.all():
         # Try / Except needed if a user misses a week
         try:
            weekscore = ScoresWeek.objects.get(Season=os.environ['PREDICTSEASON'], User=alltime.User, Week=os.environ['RESULTSWEEK'])
         except ScoresWeek.DoesNotExist:
            pass
         else:
            # Update WorstWeek if needed
            if weekscore.WeekScore < alltime.AllTimeWorst:
               alltime.AllTimeWorst = weekscore.WeekScore
            # Update BestWeek if needed
            if weekscore.WeekScore > alltime.AllTimeBest:
               alltime.AllTimeBest = weekscore.WeekScore
            # Recalculate Season Percentage
            alltimecorrect = Prediction.objects.filter(User=alltime.User, Points__gt=0).count()
            alltimepredcount = Prediction.objects.filter(User=alltime.User).exclude(Points__isnull=True).count()
            alltime.AllTimePercentage = (alltimecorrect/alltimepredcount)*100
            # Recalculate Season Average
            alltime.AllTimeAverage = alltime.AllTimeScore/ScoresWeek.objects.filter(User=alltime.User).count()
            # Recalculate Banker Average
            alltimebanktotal = 0
            for alltimebanker in Prediction.objects.filter(User=alltime.User, Banker=True):
               if isinstance(alltimebanker.Points, int):
                  alltimebanktotal += alltimebanker.Points
            alltime.AllTimeBankerAverage=alltimebanktotal/Prediction.objects.filter(User=alltime.User, Banker=True).exclude(Points__isnull=True).count()
            alltime.save()
      for c in cachestoflush:
            cache.delete(c)
   else:
      pass