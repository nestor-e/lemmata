import csv
import json

with open('idMap.json', 'r') as f:
    idMap = json.load(f)


with open('attestations.csv', 'r') as f:
    with open('attest_mod.csv', 'w') as f2:
        r = csv.reader(f)
        w = csv.writer(f2, lineterminator='\n')
        for row in r:
            id = idMap.get(row[0], "ID_CDLI")
            row = [id] + row
            w.writerow(row)
