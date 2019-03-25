### Pulls Results From NFL XML Feed
### Then Produces an Importable JSON
### File that matches the predictor.Results model
from datetime import datetime
import requests, json

outfile = open("matchesimport.json", "w")

# Below pulls xml content and stores it in 
rawschedule = requests.get('https://feeds.nfl.com/feeds-rs/schedules.json').json()

season = rawschedule['season']
schedulelist = rawschedule['gameSchedules']

tidyschedule = []
count = 0
for i in schedulelist:
    if schedulelist[count]['gameType'] == 'REG':
        ts = int(schedulelist[count]['isoTime'])/1000.0
        matchtime = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%SZ')
        innerdict = {'Week':int(schedulelist[count]['week']),'Season':int(season),'HomeTeam':schedulelist[count]['homeTeamAbbr'],'AwayTeam':schedulelist[count]['visitorTeamAbbr'],'DateTime':matchtime}
        mydict = {"model":'predictor.match', 'pk':int(schedulelist[count]['gameId']), 'fields':innerdict}
        tidyschedule.append(mydict)
    count+=1
jsonout = json.dumps(tidyschedule)
outfile.write(jsonout)
outfile.close()