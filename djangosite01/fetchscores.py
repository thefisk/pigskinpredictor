import requests
from xml.etree import ElementTree as ET

# Below pulls xml content and stores it in an XML Tree
xml = requests.get('http://www.nfl.com/liveupdate/scorestrip/ss.xml')
tree = ET.fromstring(xml.content)

# Below makes a dictionary to define following list by
for row in tree.getiterator('gms'):
    resultset = (row.attrib)

# Below makes a list of dictionaries for each game
resultsdiclist = []
for row in tree.getiterator('g'):
    resultsdiclist.append(row.attrib)