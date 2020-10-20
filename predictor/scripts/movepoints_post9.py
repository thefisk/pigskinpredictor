## Script to Move points from a game back one week
## Occasionally needed for Covid rescheduled games
## This version only to be run AFTER the ResultsWeek env var has rolled over

from predictor.models import ScoresWeek, Prediction, Match
import os

def run(*args):
    week = int(os.environ['RESULTSWEEK'])-1
    season = int(os.environ['PREDICTSEASON'])
    for gameid in args:
        match = Match.objects.get(GameID=int(gameid))
        preds = Prediction.objects.filter(Game=match)
        for pred in preds:
            try:
                thisweek = ScoresWeek.objects.get(Season=season, Week=week, User=pred.User)
            except:
                pass
            else:
                thisweek.WeekScore = thisweek.WeekScore - pred.Points
                thisweek.save()
            try:
                lastweek = ScoresWeek.objects.get(Season=season, Week=(week-1), User=pred.User)
            except:
                pass
            else:
                lastweek.WeekScore = lastweek.WeekScore + pred.Points
                lastweek.save()