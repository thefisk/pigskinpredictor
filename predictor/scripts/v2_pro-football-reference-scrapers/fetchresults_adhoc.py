### Following deprecation of nfl.com's scorestrip, this script
### uses BeautifulSoup to scrape results from pro-football-reference.com
### ready to be ingested into our custom Results model

from bs4 import BeautifulSoup
import requests, json, boto3, os, datetime
from .dictionaries.gameid_dict2020 import gameid_dict_2020 as gameid_dict
from .dictionaries.main_dicts import team_dict

def run():
    ### Tuesday 'if' loop removed so ad-hoc can be run any day
    season = os.environ['PREDICTSEASON']
    week = os.environ['RESULTSWEEK']
    week_dict = gameid_dict["Week_"+str(week)]
    url = f'https://www.pro-football-reference.com/years/{season}/games.htm'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}

    data = requests.get(url, headers=headers).text
    soup = BeautifulSoup(data, 'lxml')

    # Set Filename to include week number
    if int(week) < 10:
        filename = "resultsimport_"+season+"_0"+week+".json"
    else:
        filename = "resultsimport_"+season+"_"+week+".json"

    outfile = open(filename, "w")

    results =[]

    for game in soup.find_all('th', {'data-stat': 'week_num','csk': week}):
        innerdict = {}
        #if game is tied (pro-football references omits a <strong> tag on the winning column for tied games)
        if (game.find_next('td', {'data-stat': 'winner'})).strong == None:
            winningteam = (team_dict[game.find_next('td', {'data-stat': 'winner'}).text])
            if (game.find_next('td',{'data-stat': 'game_location'}).text == "@"):
                winner_location = "Away"
            else:
                winner_location = "Home"
            losingteam = (team_dict[game.find_next('td', {'data-stat': 'loser'}).text])
            pts_win = game.find_next('td', {'data-stat': 'pts_win'}).text
            pts_lose = game.find_next('td', {'data-stat': 'pts_lose'}).text
            innerdict['Week'] = int(week)
            innerdict['Season'] = int(season)
            if winner_location == "Away":
                innerdict['Winner'] = "Tie"
                innerdict['AwayTeam'] = winningteam
                innerdict['HomeTeam'] = losingteam
                hometeam = losingteam
                innerdict['AwayScore'] = int(pts_win)
                innerdict['HomeScore'] = int(pts_lose)
            else:
                innerdict['Winner'] = "Tie"
                innerdict['AwayTeam'] = losingteam
                innerdict['HomeTeam'] = winningteam
                hometeam = winningteam
                innerdict['AwayScore'] = int(pts_lose)
                innerdict['HomeScore'] = int(pts_win)
        # if game not tied
        else:    
            winningteam = (team_dict[game.find_next('td', {'data-stat': 'winner'}).text])
            if (game.find_next('td',{'data-stat': 'game_location'}).text == "@"):
                winner_location = "Away"
            else:
                winner_location = "Home"
            losingteam = (team_dict[game.find_next('td', {'data-stat': 'loser'}).text])
            pts_win = game.find_next('td', {'data-stat': 'pts_win'}).text
            pts_lose = game.find_next('td', {'data-stat': 'pts_lose'}).text
            innerdict['Week'] = int(week)
            innerdict['Season'] = int(season)
            if winner_location == "Away":
                innerdict['Winner'] = "Away"
                innerdict['AwayTeam'] = winningteam
                innerdict['HomeTeam'] = losingteam
                hometeam = losingteam
                innerdict['AwayScore'] = int(pts_win)
                innerdict['HomeScore'] = int(pts_lose)
            else:
                innerdict['Winner'] = "Home"
                innerdict['AwayTeam'] = losingteam
                innerdict['HomeTeam'] = winningteam
                hometeam = winningteam
                innerdict['AwayScore'] = int(pts_lose)
                innerdict['HomeScore'] = int(pts_win)
        outerdict = {}
        outerdict['model'] = "predictor.results"
        outerdict['pk'] = week_dict[hometeam]
        outerdict['fields'] = innerdict
        results.append(outerdict)
        
    jsonout = json.dumps(results)
    outfile.write(jsonout)
    outfile.close()

    # Upload to S3
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket,filename)
    s3path = 'data/'+filename
    s3.Object(bucket, s3path).upload_file(Filename=filename)