### Pulls Results From NFL XML Feed
### Then Produces an Importable JSON
### File that matches the predictor.Results model

import requests, json
from xml.etree import ElementTree as ET

# Below pulls xml content and stores it in an XML Tree
xml = requests.get('http://www.nfl.com/liveupdate/scorestrip/ss.xml')
tree = ET.fromstring(xml.content)

# Below makes a dictionary to define following list by
for row in tree.getiterator('gms'):
    resultset = (row.attrib)
week = resultset['w']
season = resultset['y']

# Set Filename to include week number
if int(week) < 10:
    filename = "resultsimport_"+season+"_0"+week+".json"
else:
    filename = "resultsimport_"+season+"_"+week+".json"

outfile = open(filename, "w")

# Below makes a list of dictionaries for each game
resultsdiclist = []
for row in tree.getiterator('g'):
    resultsdiclist.append(row.attrib)
#outfile.write(str(resultsdiclist))
#outfile.close()
tidyresults = []
count = 0
for i in resultsdiclist:
    awayscore = int(resultsdiclist[count]['vs'])
    homescore = int(resultsdiclist[count]['hs'])
    if homescore == awayscore:
        winner = 'Tie'
    elif homescore > awayscore:
        winner = 'Home'
    else:
        winner = 'Away'
    innerdict = {'Winner': winner,'Week':int(week),'Season':int(season),'HomeTeam':resultsdiclist[count]['h'],'AwayTeam':resultsdiclist[count]['v'],'HomeScore':homescore,'AwayScore':awayscore}
    mydict = {"model":'predictor.results', 'pk':int(resultsdiclist[count]['eid']), 'fields':innerdict}
    tidyresults.append(mydict)
    count+=1
jsonout = json.dumps(tidyresults)
outfile.write(jsonout)
outfile.close()