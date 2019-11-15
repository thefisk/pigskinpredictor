### Pulls Results From NFL XML Feed
### Then Produces an Importable JSON
### File that matches the predictor.Results model
from datetime import datetime
import requests, json, boto3, os

def run():
    # Below pulls xml content and stores it in 
    rawschedule = requests.get('https://feeds.nfl.com/feeds-rs/schedules.json').json()

    season = rawschedule['season']
    schedulelist = rawschedule['gameSchedules']

    filename = "matchesimport_" + str(season) + ".json"
    outfile = open(filename, "w")

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

    # Upload to S3
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket,filename)
    s3path = 'data/'+filename
    s3.Object(bucket, s3path).upload_file(Filename=filename)