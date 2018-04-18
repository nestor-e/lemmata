import csv
import sys
from fuzzywuzzy import fuzz
import progressbar


def loadLemmata(lemmataFile):
    pn = set()
    gn = set()
    other = set()
    with open(lemmataFile, 'r') as input:
        read = csv.reader(input, delimiter='\t')
        for row in read:
            if row[2] == 'PN':
                pn.add(row[1])
            elif row[2] == 'GN':
                gn.add(row[1])
            else:
                other.add(row[1])
    return (pn, gn, other)


def loadNames(namesFile):
    names = set()
    with open(namesFile, 'r') as input:
        read = csv.reader(input)
        for row in read:
            names.add(row[1])
    return names

def maxRatio(name, options):
    max = 0
    for token in options:
        ratio = fuzz.ratio(name, token)
        if ratio > max:
            max = ratio
    return max

def matchCount(names, lemPN, lemGN, lemOTHER):
    (matchPN, matchGN, matchOTHER, matchNONE) = (0, 0, 0, 0)
    threshold = 90
    bar = progressbar.progressbar(names)
    #distlog = open('dist.log', 'w');
    for name in bar:
        pnRatio = maxRatio(name, lemPN)
        gnRatio = maxRatio(name, lemGN)
        otherRatio = maxRatio(name, lemOTHER)
        m = max(pnRatio, gnRatio, otherRatio)
        #print(m, file=distlog)
        if m < threshold:
            matchNONE += 1
        elif m == pnRatio:
            matchPN += 1
        elif m == gnRatio:
            matchGN += 1
        else:
            matchOTHER += 1

    #distlog.close()
    return (matchPN, matchGN, matchOTHER, matchNONE)


def main(nameFile, lemFile):
    (pnSet, gnSet, otherSet) = loadLemmata(lemFile)
    names = loadNames(nameFile)
    (pn, gn, other, none) = matchCount(names, pnSet, gnSet, otherSet)
    print('PN match : {}/{}'.format(pn, len(names)))
    print('GN match : {}/{}'.format(gn, len(names)))
    print('OTHER match : {}/{}'.format(other, len(names)))
    print('NONE match : {}/{}'.format(none, len(names)))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
