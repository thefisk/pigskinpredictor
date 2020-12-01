## v3 Results Fetch Script
## Uses ESPN JSON API

import requests, json, os, boto3, operator
from datetime import datetime, timedelta
from .dictionaries.gameid_dict2020 import gameid_dict_2020 as gameid_dict

def run():
    ## Only run on a Thursday
    if datetime.today().isoweekday() == 4:
        week = os.environ['RESULTSWEEK']
        season = os.environ['PREDICTSEASON']
        week_dict = gameid_dict["Week_"+str(week)]

        if int(week) < 10:
            filename = "resultsimport_"+season+"_0"+week+".json"
        else:
            filename = "resultsimport_"+season+"_"+week+".json"

        outfile = open(filename, "w")

        # Weeks param doesn't seem to work on ESPN API so have to use date range
        # ESPN uses Zulu time so MNF will be a Tuesday datetime, hence including today in range
        today = datetime.today().strftime('%Y%m%d')
        thurs = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')
        source = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={thurs}-{today}"

        rawjson = requests.get(source).json()

        results = []

        for game in rawjson['events']:
            team1 = {}
            team1['team'] = game['competitions'][0]['competitors'][0]['team']['abbreviation']
            team1['score'] = int(game['competitions'][0]['competitors'][0]['score'])
            team1['location'] = game['competitions'][0]['competitors'][0]['homeAway']
            team2 = {}
            team2['team'] = game['competitions'][0]['competitors'][1]['team']['abbreviation']
            team2['score'] = int(game['competitions'][0]['competitors'][1]['score'])
            team2['location'] = game['competitions'][0]['competitors'][1]['homeAway']
            innerdict = {}
            innerdict["Week"] = int(week)
            innerdict["Season"] = int(season)
            if team1['location'] == "home":
                innerdict["HomeTeam"] = team1['team']
                innerdict["AwayTeam"] = team2['team']
                innerdict["HomeScore"] = team1['score']
                innerdict["AwayScore"] = team2['score']
            else:
                innerdict["HomeTeam"] = team2['team']
                innerdict["AwayTeam"] = team1['team']
                innerdict["HomeScore"] = team2['score']
                innerdict["AwayScore"] = team1['score']
            if team1['score'] == team2['score']:
                innerdict["Winner"] = "Tie"
            elif (team1['score']) > (team2['score']):
                innerdict["Winner"] = "Home"
            else:
                innerdict["Winner"] = "Away"
            outerdict = {}
            outerdict["model"] = "predictor.results"
            outerdict["pk"] = week_dict[innerdict['HomeTeam']]
            outerdict["fields"] = innerdict
            results.append(outerdict)

        # ESPN Uses different short names for Washington and LA Rams to NFL.com
        # Loop through and rename them to ensure they match our model
        # Otherwise the import won't work!

        for result in results:
            if (result['fields']['HomeTeam']) == "WSH":
                result['fields']['HomeTeam'] = "WAS"
            if (result['fields']['HomeTeam']) == "LAR":
                result['fields']['HomeTeam'] = "LA"
            if (result['fields']['AwayTeam']) == "WSH":
                result['fields']['AwayTeam'] = "WAS"
            if (result['fields']['AwayTeam']) == "LAR":
                result['fields']['AwayTeam'] = "LA"

        sortedresults = sorted(results, key=lambda k: k['pk'])
        jsonout = json.dumps(sortedresults)
        outfile.write(jsonout)
        outfile.close()

        # Upload to S3
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket,filename)
        s3path = 'data/'+filename
        s3.Object(bucket, s3path).upload_file(Filename=filename)
    else:
        pass