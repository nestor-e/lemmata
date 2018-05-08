import csv
import json
import sys
import re
import Levenshtein as Lv # package python-Levenshtein


smbolBreaks = re.compile(r"\s|[-\[\]?]")

def wrdCompare(target, word):
    sylables = word.split("-")
    minDistance = 2**30
    for first in range(len(sylables)):
        for last in range(first + 1, len(sylables) + 1):
            comp = "-".join(sylables[first:last])
            dist = Lv.distance(comp, target)
            minDistance = min(minDistance, dist)
    return minDistance

#TODO : Better algorithim
#Find substring of source most closely matching target
def findMatch(target, source):
    target = target.lower()
    source = source.lower()
    options = source.split()
    val = [wrdCompare(target, opt) for opt in options]
    cI = val.index(min(val))
    dist = val[cI]
    selected = options[cI]

    if dist > len(selected) or len(selected) < 3 or selected == "[...]":
        return None
    else:
        # print("{}: {} -> {}  (from {})".format(val[cI], target, options[cI], source))
        return selected

def getAttestData(attestFile):
    bParts = re.compile(r"(o|r|s)\.(i*)")
    bParts2 = re.compile(r"le?\.ed\.(i*)")
    aData = {}

    with open(attestFile, 'r') as iF:
        attestReader = csv.DictReader(iF)
        for row in attestReader:
            key   = row['ID_CDLI']
            if key not in aData:
                aData[key] = {}
            pText = row['Part text']
            lNum  = row['Line']
            label = row['PN or GN']
            name = row['PN/GN as attested']
            m  = bParts.search(pText)
            m2 = bParts2.search(pText)
            if  m:
                lineLabel = None
                if m.group(1) == 'o':
                    lineLabel = 'obverse'
                elif m.group(1) == 'r':
                    lineLabel = 'reverse'
                else:
                    lineLabel = 'seal'
                col = max(1, len(m.group(2)))
            elif m2:
                lineLabel = 'left'
                col = max(1, len(m2.group(1)))
            else:
                lineLabel = None

            if lineLabel != None:
                locKey = "{}:{}:{}".format(lineLabel, col, lNum)
                if locKey not in aData[key]:
                    aData[key][locKey] =[]
                aData[key][locKey].append({'texOrig' : name, 'label' : label})
    return aData


def create_corpus(jsonFile, aData, outFile):
    lemLine = re.compile(r"^#lem:")
    lemName = re.compile(r"([PGRMDWT]N)")

    lData = {}
    with open(jsonFile, "r") as iF:
        tabs  = json.load(iF)

    with open(outFile, 'w') as oF:
        cWrite = csv.DictWriter(oF, ["Id BDTNS","Provenance","Date","Seal","Id Line","Part text","Line","Text"],restval="N", lineterminator='\n')
        cWrite.writeheader()
        lineId = 0
        for tab in tabs:
            tabKey = tab['idCDLI']
            # print('\n',tabKey)
            for side in tab['sides']:
                lineLabel = side['side'].lower()
                for colNum in range(len(side['content'])):
                    col = side['content'][colNum]
                    for lineNum in range(len(col['lines'])):
                        lineId += 1
                        lineIdTex = "L{:06d}".format(lineId)
                        line = col['lines'][lineNum]
                        locId = "{}:{}:{}".format(lineLabel, colNum + 1, lineNum + 1)
                        cRow = {"Id BDTNS" : tabKey, "Id Line" : lineIdTex, "Part text" : "{}:{}".format(lineLabel, colNum + 1), "Text" : line['text']}
                        cWrite.writerow(cRow)
                        if (tabKey in aData) and (locId in aData[tabKey]):
                            # print(locId)
                            for attest in aData[tabKey][locId]:
                                attest['lineId'] = lineIdTex
                                attest['texCDLI'] = findMatch(attest['texOrig'], line['text'])
                                attest['wholeLine'] = line['text']


def create_attest(aData, outFile):
    with open(outFile, 'w') as oF:
        cWrite = csv.DictWriter(oF, [   "Id BDTNS","Id Line", "Part text", "Line","Text",
                                        "PN/GN as attested", "Id PN/GN as attested", "PN/GN Normalized",
                                        "Id PN/GN normalized", "PN or GN", "Seal", "Date" ], restval="N", lineterminator='\n')
        cWrite.writeheader()
        for tabKey in aData:
            for locID in aData[tabKey]:
                for attest in aData[tabKey][locID]:
                    if 'lineId' in attest and attest['texCDLI'] != None:
                        cRow = {"Id BDTNS" : tabKey,
                                "Id Line" : attest['lineId'],
                                "PN/GN as attested" : attest['texCDLI'],
                                "PN or GN" : attest['label'],
                                "Text" : attest['wholeLine']}
                        cWrite.writerow(cRow)


aData = getAttestData("attest_mod.csv")
create_corpus("gs_full.json", aData, "gs_corpus.csv")
create_attest(aData, 'gs_attestations.csv')
