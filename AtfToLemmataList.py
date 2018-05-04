#arguments: input ATF file, output lemmata csv, output psudo-atf
import re
import sys

verbose = False


lemLine = re.compile(r"^#lem:")
txtLine = re.compile(r"^\d+[.,']* ?,?(.*)")
txtFilter = re.compile(r"<<\S*?>>")

def splitTxt(line):
    m = txtLine.match(line)
    if m != None:
        temp = m.group(1).split()
        out = []
        for token in temp:
            if not txtFilter.match(token):
                out.append(token)
        return out
    else:
        return line.split()[1:]

def splitLem(line):
    line = line[5:]
    out = []
    lineParts = line.split(";")
    for i in range(len(lineParts)):
        tmp = lineParts[i].strip()
        if len(tmp) > 0:
            out.append(tmp)
    return out

def lemGet(txtLine, lemLine):
    txtTokens = splitTxt(txtLine)
    lemTokens = splitLem(lemLine)
    out  = []
    if(len(txtTokens) != len(lemTokens)):
        if verbose:
            print("Warning: Token length mismatch")
            print(txtLine)
            print(lemLine)
            print(txtTokens)
            print(lemTokens)
            print()
            print()
    else:
        for i in range(len(txtTokens)):
            out.append( {'txt' : txtTokens[i], 'lem' : lemTokens[i]} )
    return out

def main(inFile, outFile, snerFile):
    # {txt , lem, pos}
    lemmata = []
    with open(inFile, 'r', encoding='utf-8') as src:
        lastLine = next(src).strip()
        for line in src:
            if lemLine.match(line):
                lemmata += lemGet(lastLine.strip(), line.strip())
            lastLine = line

    seenWords = set()

    with open(snerFile, 'w') as sOut:
        print("&P101001", file=sOut)
        pos = 1
        for lem in lemmata:
            if(lem['txt'] not in seenWords):
                lem['pos'] = pos
                pos += 1
                print("1. {}".format(lem['txt']), file=sOut)
                seenWords.add(lem['txt'])

    with open(outFile, 'w') as out:
        for lem in lemmata:
            if 'pos' in lem:
                print("{}\t{}\t{}".format(lem['pos'], lem['txt'], lem['lem']), file=out)

    print(len(seenWords), "lemmata recovered")

if __name__ == "__main__":
	main(sys.argv[1], sys.argv[2], sys.argv[3])
