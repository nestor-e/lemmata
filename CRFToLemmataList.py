#arguments: input CRF bar atf file, output lemmata csv, output psudo-atf
import re
import sys

def getLemma(fname):
    lem = {}    # name : {label : count, ...}
    with open(fname, 'r') as txt:
        for line in txt:
            line = line.split('\t')
            if len(line) == 2:
                word = line[0].strip()
                label = line[1].strip()
                if word not in lem:
                    lem[word] = {}
                if label not in lem[word]:
                    lem[word][label] = 0
                lem[word][label] += 1
    return lem

def stringifyLemLabels(labelDict):
    return "|".join([key for key in labelDict])


def main(inFile, outFile, snerFile):
    lemmata = getLemma(inFile)

    with open(outFile, 'w') as csv:
        with open(snerFile, 'w') as atf:
            print("&P101001", file=atf)
            pos = 1
            for wrd in lemmata:
                print("1. {}".format(wrd), file=atf)
                print("{}\t{}\t{}".format(pos, wrd, stringifyLemLabels(lemmata[wrd])), file=csv )
                pos += 1
    print(len(lemmata), "lemmata recovered")

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2], sys.argv[3])
