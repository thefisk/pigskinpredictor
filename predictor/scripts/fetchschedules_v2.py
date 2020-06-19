### Following deprecation of feeds.nfl.com this script
### uses BeautifulSoup to scrape schedule info from pro-football-reference.com
### and ingest into our custom Match model

from bs4 import BeautifulSoup
import requests
import requests, json, boto3, os

url = 'https://www.pro-football-reference.com/years/2020/games.htm'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}

with open('/mnt/f/PFR.html') as html:
    soup = BeautifulSoup(html, 'lxml')

team_dict = {
    'Arizona Cardinals': 'ARI',
    'Atlanta Falcons': 'ATL',
    'Baltimore Ravens': 'BAL',
    'Buffalo Bills': 'BUF',
    'Carolina Panthers': 'CAR',
    'Chicago Bears': 'CHI',
    'Cincinnati Bengals': 'CIN',
    'Cleveland Browns': 'CLE',
    'Dallas Cowboys': 'DAL',
    'Denver Broncos': 'DEN',
    'Detroit Lions': 'DET',
    'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU',
    'Indianapolis Colts': 'IND',
    'Jacksonville Jaguars': 'JAX',
    'Kansas City Chiefs': 'KC',
    'Las Vegas Raiders': 'LV', 
    'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LA',
    'Miami Dolphins': 'MIA',
    'Minnesota Vikings': 'MIN',
    'New England Patriots': 'NE',
    'New Orleans Saints': 'NO',
    'New York Giants': 'NYG',
    'New York Jets': 'NYJ',
    'Philadelphia Eagles': 'PHI',
    'Pittsburgh Steelers': 'PIT',
    'San Francisco 49ers': 'SF',
    'Seattle Seahawks': 'SEA',
    'Tampa Bay Buccaneers': 'TB',
    'Tennessee Titans': 'TEN',
    'Washington Redskins': 'WAS'
}

calendar_dict = {
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12',
    'January': '01'
}

schedule=[]
season = "2020"

filename = "matchesimport_" + str(season) + ".json"
outfile = open(filename, "w")

for week in range(1,18):
    game = soup.find('th', {"csk": week})
    for game_num in range(1, len(soup.find_all('th', {"csk": week}))+1):
        if week < 10:
            matchweek = "0"+str(week)
        else:
            matchweek = str(week)
        if game_num < 10:
            game_ref = "0"+str(game_num)
        else:
            game_ref = str(game_num)
        match_id = season+matchweek+game_ref
        date = game.find_next('td', {"data-stat":"boxscore_word"}).text
        month = calendar_dict[date.split()[0]]
        day = date.split()[1]
        if int(day) < 10:
            day = "0"+str(day)
        fulldate = season+"-"+month+"-"+day
        away_team = team_dict[game.find_next('td', {"data-stat":"visitor_team"}).text]
        home_team = team_dict[game.find_next('td', {"data-stat":"home_team"}).text]
        gametime = game.find_next('td', {"data-stat":"gametime"}).text
        if ((gametime.split(':')[1].split()[1]) == "AM") or (int(gametime.split(':')[0]) == 12):
            hour = str(int(gametime.split(':')[0]))
        else:
            hour = str(int(gametime.split(':')[0])+12)
        minute = gametime.split(':')[1].split()[0]
        datetime = fulldate+" "+hour+":"+minute+":00Z"
        innerdict = {'Week':int(week),'Season':int(season),'HomeTeam':home_team,'AwayTeam':away_team,'DateTime':datetime}
        mydict = {"model":'predictor.match', 'pk':int(match_id), 'fields':innerdict}
        schedule.append(mydict)
        game = game.find_next('th', {"csk": week})

jsonout = json.dumps(schedule)
outfile.write(jsonout)
outfile.close()

# Upload to S3
bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
s3 = boto3.resource('s3')
obj = s3.Object(bucket,filename)
s3path = 'data/'+filename
s3.Object(bucket, s3path).upload_file(Filename=filename)