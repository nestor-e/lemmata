import urllib.request
import re
import json
import progressbar
import shutil

ids = []
with open('ur3_parsed.json', 'r') as idSource:
    tabData = json.load(idSource)
    for tab in tabData:
        ids.append(tab['idCDLI'])


pNum = re.compile(r"P(\d{6})")

urlBase = "https://cdli.ucla.edu/search/revhistory.php/?txtpnumber={}&"
dir = "./HistoricalData/{}.txt"

idBar = progressbar.progressbar(ids)
for id in idBar:
    idNum = pNum.match(id).group(1)
    with urllib.request.urlopen(urlBase.format(idNum)) as response:
        with open(dir.format(id), 'wb') as store:
            shutil.copyfileobj(response, store)
