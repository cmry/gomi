#!/usr/bin/env python

__author__ = 'chris'
__version__ = '15.01'

from glob import glob
import subprocess
import sys

class CorpusCleaner:

    def __init__(self, i):
        """ These are _very_ ugly hot fixes to batch process the WSJ corpus to
            ABL standard and make them compatible with the output. Some stuff
            has been removed again in ftuk, please rewrite this if used again! """

        self.perl_call()
        self.fix()
        self.i = i

    def perl_call(self):
        with open('wjb10.gold.tmp', 'ab+') as f:
            fl = glob('/home/nlp_project/TREEBANK_3/parsed/mrg/wsj/*/*.mrg')
            fl.sort()
            for filename in fl:
                subprocess.Popen(["/home/nlp_project/extract_grammar_wsj.pl",
                                  "-i", filename, "-o", "-", "-l"], stdout=f)

    def fix(self):
        with open('wjb10.gold', 'ab+') as outp:
            with open('wbj10.gold.tmp', 'ab+') as f2:
                for line1 in f2.readlines():
                    line1 = line1.replace('  @@@  ', ' @@@ ')
                    line1 = line1.replace(',', ', ')  # this was removed in tagger.py
                    line1 = line1.replace(')', ') ')  # this was removed in tagger.py
                    line1 = line1.replace('\n', '')
                    if line1.startswith('@@@'):
                        pass
                    else:
                        outp.write(line1+'\n')
        subprocess.call(["rm", "wjb10.gold.tmp"])

def main():
    cc = CorpusCleaner()
    print "~~ Corpus has been fixed!"
    print "   Outputted to wjb10.gold"

if __name__ == '__main__':
    main()