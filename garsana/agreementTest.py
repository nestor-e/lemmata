import sys
import csv
import json
import re


def getLemmataSet(jsonFile):
    lemLine = re.compile(r"^#lem:")
    lemName = re.compile(r"([PGRMDWT]N)")

    lData = {}
    with open(jsonFile, "r") as iF:
        tabs  = json.load(iF)

    for tab in tabs:
        tabKey = tab['idCDLI']
        lData[tabKey] = {}
        for side in tab['sides']:
            lineLabel = side['side'].lower()
            for colNum in range(len(side['content'])):
                col = side['content'][colNum]
                for lineNum in range(len(col['lines'])):
                    line = col['lines'][lineNum]
                    locId = "{}:{}:{}".format(lineLabel, colNum + 1, lineNum + 1)
                    if "comments" in line:
                        labels = []
                        for comment in line['comments']:
                            if lemLine.match(comment):
                                for nameItm in lemName.findall(comment):
                                    if nameItm not in ['PN', 'GN']:
                                        nameItm = 'ON'
                                    labels.append(nameItm)
                        lData[tabKey][locId] = labels
    return lData


def getAttestSet(attestFile):
    bParts = re.compile(r"(o|r|s)\.(i*)")
    bParts2 = re.compile(r"le?\.ed\.(i*)")
    aData = {}
    blackList = set()

    with open(attestFile, 'r') as iF:
        attestReader = csv.DictReader(iF)
        for row in attestReader:
            key   = row['ID_CDLI']
            if key not in aData:
                aData[key] = {}
            pText = row['Part text']
            lNum  = row['Line']
            label = row['PN or GN']
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
                blackList.add(key)

            locId = "{}:{}:{}".format(lineLabel, col, lNum)
            if locId not in aData[key]:
                aData[key][locId] = []
            aData[key][locId].append(label)
    return (aData, blackList)



def main(jsonFile, attestFile):
    lData = getLemmataSet(jsonFile)
    (aData, blacklist) = getAttestSet(attestFile)

    for tabKey in aData:
        if tabKey not in lData:
            blacklist.add(tabKey)

    for tabKey in blacklist:
        if tabKey in aData:
            del aData[tabKey]
        if tabKey in lData:
            del lData[tabKey]

    #                   Lemmata
    #           PN     GN     ON    MISS
    #          --------------------------
    # A  PN   |     |      |      |      |
    # t       |-----|------|------|------|
    # t  GN   |     |      |      |      |
    # e       |-----|------|------|------|
    # s  MISS |     |      |      |   0  |
    # t        --------------------------

    (lemTotal, attestTotal) = (0, 0)
    grid = {'PN'   : {'PN' : 0, 'GN' : 0, 'ON' : 0, 'MISS' : 0},
            'GN'   : {'PN' : 0, 'GN' : 0, 'ON' : 0, 'MISS' : 0},
            'MISS' : {'PN' : 0, 'GN' : 0, 'ON' : 0, 'MISS' : 0}}

    for tabKey in aData:
        tabAtt = aData[tabKey]
        tabLem = lData[tabKey]
        for loc in tabAtt:
            temp = tabLem.get(loc, [])
            temp = temp[:]
            for label in tabAtt[loc]:
                attestTotal += 1
                if label in temp:
                    temp.remove(label)
                    grid[label][label] += 1
                    lemTotal += 1
                elif len(temp) > 0:
                    lemLabel = temp.pop(0)
                    grid[label][lemLabel] += 1
                    lemTotal += 1
                else:
                    grid[label]['MISS'] += 1
            for lemLabel in temp:
                grid['MISS'][lemLabel] += 1
                lemTotal += 1

    print(lemTotal, attestTotal)
    print(grid)



if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
