import os
import re
import json
from bs4 import BeautifulSoup as soup

DIR = "./HistoricalData/"

revStart = re.compile(r"^#atf:")
lemLine = re.compile(r"^#lem:")
nameLem = re.compile(r"[PG]N")


def getLemmataPNCount(fName):
    with open(DIR + fName, 'r') as source:
        text = soup(source, 'html.parser').get_text()
        text = text.splitlines()
        revCount = 0
        tempCount = 0
        mCount = 0
        for line in text:
            if revStart.match(line):
                mCount = max(mCount, tempCount)
                tempCount = 0
            elif lemLine.match(line):
                tempCount += len(nameLem.findall(line))
    return max(mCount, tempCount)

def countPNjson(tab):
    count = 0
    for side in tab['sides']:
        for r in side['content']:
            for line in r['lines']:
                if 'attestations' in line:
                    count += len(line['attestations'])
    return count



def main():
    with open("ur3_parsed.json") as k:
        tabData = json.load(k)
    files = os.listdir(DIR)
    delta = {}
    for tab in tabData:
        fName = tab['idCDLI'] + '.txt'
        if fName in files:
            lemCount = getLemmataPNCount(fName)
            snerCount = countPNjson(tab)
            diff = snerCount - lemCount
            if diff in delta:
                delta[diff] += 1
            else:
                delta[diff] = 1
    keylist = sorted(delta.keys())

    for key in keylist:
        print("{}\t{}".format(key, delta[key]))
main()
