from bs4 import BeautifulSoup as bSoup
import os
import re
from operator import itemgetter

revLine = re.compile(r"^\d{4}-\d{2}-\d{2}")
lemLine  = re.compile(r"^#lem:")


def convertFile(dir, fName, outputStream):
    lines = []
    with open(dir + fName, 'r', encoding='utf-8') as src:
        htmlRep = bSoup(src, 'html.parser')
        for line in htmlRep.stripped_strings:
            lines.append(line)

    revData = []
    revStart = -1
    revLemCount = 0
    for i in range(len(lines)):
        line = lines[i]
        # print(i, ":", line )
        if revLine.match(line):
            if revStart >= 0:
                revData.append( (revStart, i, revLemCount) )
            revStart = i
            revLemCount = 0
        elif lemLine.match(line):
            revLemCount += 1
    if revStart >= 0:
        revData.append((revStart, len(lines), revLemCount))
    revData.sort(key=itemgetter(2), reverse=True)
    # print(revData)
    if len(revData) > 0:
        selectedRev = revData[0]
        for line in lines[ selectedRev[0] + 1 : selectedRev[1]]:
            print(line, file=outputStream)
        return selectedRev[2] > 0
    return False


def main(targetFile, dataDir):
    fOut = open(targetFile, 'w', encoding='utf-8')
    lemCount = 0
    tabs = 0
    for fName in os.listdir(dataDir):
        tabs += 1
        hasLem = convertFile(dataDir, fName, fOut)
        if hasLem :
            lemCount += 1
        print(file=fOut)
    fOut.close()
    print("{} / {} tablet with lemmata".format(lemCount, tabs))


main("lemmata.atf" , "./HistoricalData/")
