### Since NFL Deprecated their results feed, results
### will be imported using web scraping for now.

### That means individual GameID primary keys are missing from source data.
### This script will, once per season,
### create a dictionary containing weekly GameIDs by Home Team.

### That dictionary will be referenced by the results scraper to match results
### to GameIDs, so they are ready for importing.

import json

season = "2020"
jsonfile = "matchesimport_"+season+".json"

with open(jsonfile) as jsonmatches:
    matchlist = json.load(jsonmatches)

filename = "gameid_dict" + str(season) + ".py"
path = './dictionaries' "//"
fullpath = path+filename
outfile = open(fullpath, "w")

games_2020 = {}
   
for week in range(1,18):
    dict_index = "Week_"+str(week)
    games_2020[dict_index] = {}
    for fixture in matchlist:
        if fixture['fields']['Week'] == week:
            home = fixture['fields']['HomeTeam']
            games_2020[dict_index][home] = fixture['pk']

outfile.write("gameid_dict_"+season+" = "+str(games_2020))
outfile.close()