### Schedule Fetcher now uses ESPN API
### Data is in easy-to-digest JSON format at source
### Means Game PKs will now match the results data source
### This will remove the need for messy dictionary lookups
from django.core.management.base import BaseCommand
from datetime import datetime as dt
import requests, json

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Use datetime module to get current year
        season = dt.now().year

        base_url = f'http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={season}'

        schedule=[]

        filename = "schedule.json"
        outfile = open(filename, "w")

        # Range extended by 1 in 2021 for 17 game season (over 18 weeks)
        for week in range(1,19):
            url = base_url + f'&week={week}'
            rawjson = requests.get(url).json()
            for game in rawjson['events']:
                gameid = game['id']
                teamdict = {}
                teamdict[game['competitions'][0]['competitors'][0]['homeAway']] = game['competitions'][0]['competitors'][0]['team']['abbreviation']
                teamdict[game['competitions'][0]['competitors'][1]['homeAway']] = game['competitions'][0]['competitors'][1]['team']['abbreviation']
                datetime = game['date']
                innerdict = {'Week':int(week),'Season':int(season),'HomeTeam':teamdict['home'],'AwayTeam':teamdict['away'],'DateTime':datetime}
                mydict = {"model":'predictor.match', 'pk':int(gameid), 'fields':innerdict}
                schedule.append(mydict)

        jsonout = json.dumps(schedule)
        outfile.write(jsonout)
        outfile.close()