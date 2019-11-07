import os, json
from predictor.models import Team, Results

def run():
   fileweek = os.environ['PREDICTWEEK']
   fileseason = os.environ['PREDICTSEASON']
   filename = 'resultsimport_'+fileseason+'_'+fileweek+'.json'

   with open(filename) as results_json:
      data = json.load(results_json)

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