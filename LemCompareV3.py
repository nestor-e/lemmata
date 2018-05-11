#arguments : lemmata csv, SNER target_atf.Key, SNER atf_prediction.RT
import sys

nameMarkers = ['PN', 'GN']

def checkLem(lem):
    isName = False
    labels = lem.split("|")
    for label in labels:
        if label in nameMarkers:
            isName = True
    return isName

def compileResults(idxFile, resFile):
    idx = []
    res = []
    with open(idxFile, 'r') as f:
        idx = f.read().splitlines()
    with open(resFile, 'r') as f:
        res = f.read().splitlines()

    q = {}
    wrd = {}
    for i in range(len(idx)):
        parts = idx[i].split('\t')
        lineID = parts[1]
        isName = res[i].strip() == "1"
        if not lineID in q:
            q[lineID] = []
            wrd[lineID] = []
        if isName not in q[lineID]:
            q[lineID].append(isName)
        wrd[lineID].append(parts[3])
    return (q, wrd)

def main(lemFile, snerIdxFile, snerResFile):
    (res, wordMap) = compileResults(snerIdxFile, snerResFile)
    (truePositive, trueNegative, falsePositive, falseNegative) = (0, 0, 0, 0)
    undecided = 0
    total = 0

    with open(lemFile, 'r') as lemmata:
        for line in lemmata:
            total += 1
            parts = line.split('\t')
            loc = parts[0]
            wrdSNER = wordMap.get(loc, [])
            if parts[1] not in parts[1]:
                print("{} -> {}".format(parts[1], wrdSNER))
            isName = checkLem(parts[2])

            if loc in res:
                r = res[loc]
            else:
                r = [False]    #  SNER ommits - and ... from its results as known non-name

            if (True in r) and (False in r):
                undecided += 1
            elif (True in r):
                if isName:
                    truePositive += 1
                else:
                    falsePositive += 1
            else:
                if isName:
                    falseNegative += 1
                else :
                    trueNegative += 1
    print("Total tokens   : {:6d} : 100.000%".format(total) )
    print("Undecided      : {:6d} : {:7.3f}%".format(undecided, undecided / total * 100.0) )
    print("True Positive  : {:6d} : {:7.3f}%".format(truePositive, truePositive / total * 100.0) )
    print("True Negative  : {:6d} : {:7.3f}%".format(trueNegative, trueNegative / total * 100.0) )
    print("False Positive : {:6d} : {:7.3f}%".format(falsePositive, falsePositive / total * 100.0) )
    print("False Negative : {:6d} : {:7.3f}%".format(falseNegative, falseNegative / total * 100.0) )


main(sys.argv[1], sys.argv[2], sys.argv[3])
