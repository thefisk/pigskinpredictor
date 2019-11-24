### Script to read saved results json file
### and store in backend database in Results table
### _Adhoc version for manual use only

import os, json, boto3
from predictor.models import Team, Results

def run():
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