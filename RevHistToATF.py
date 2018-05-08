# Args : Output File, data directory

import os
import re
from bs4 import BeautifulSoup as bSoup
from operator import itemgetter
import sys

revLine = re.compile(r"\d{4}-\d{2}-\d{2}")
tabLine = re.compile(r"&P\d{6}")
imbededLemDetect = re.compile(r"(\S)#lem:")
imbededTxtDetect = re.compile(r"(;[^;\n\r]*?)(\d+\.)")
imbededTxtDetect2 = re.compile(r"(#lem: \S+)(\d+\.)")
lemLine  = re.compile(r"^#lem:")

def insertNewline(match):
    return "\n" + match.group(0)

def unEmbed1(match):
    return match.group(1) + "\n#lem:"

def unEmbed2(match):
    return match.group(1) + "\n" + match.group(2)

def convertFile(dir, fName, outputStream):
    with open(dir + fName, 'r', encoding='utf-8') as src:
        text = bSoup(src, 'html.parser').get_text()
    text = revLine.sub(insertNewline, text)
    text = tabLine.sub(insertNewline, text)
    text = imbededLemDetect.sub(unEmbed1, text)
    text = imbededTxtDetect.sub(unEmbed2, text)
    text = imbededTxtDetect2.sub(unEmbed2, text)
    lines = text.splitlines()

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
    rem = len(os.listdir(dataDir))
    for fName in os.listdir(dataDir):
        tabs += 1
        hasLem = convertFile(dataDir, fName, fOut)
        if hasLem :
            lemCount += 1
        rem -= 1
        if rem % 1000 == 0:
            print(rem, "remaining")
        print(file=fOut)
    fOut.close()
    print("{} / {} tablet with lemmata".format(lemCount, tabs))

if __name__ == "__main__":
	main(sys.argv[1] , sys.argv[2])
