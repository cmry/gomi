#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 1.2'
__doc__ = """ Ftuk!

 Usage:
    ftuk [-v] freq --wsjlen=I [--cor] [--inc] [--tot] [--perc] [--ngr=N] [--amb] <input>...
    ftuk [-v] fix <input>
    ftuk (-h | --help)
    ftuk --version

 Arguments:
    freq                outputs the POS frequencies for one or multiple
                        corpora to the oupt/res.tex file
    fix                 recompiles the old WSJ corpus to a format usable
                        by ABL, old function, better not use
 Freq:
    --cor               list the column with correctly learned tags
    --inc               list the column with incorrectly learned tags
    --tot               list the column with the total amount of tags
    --wsjlen=I          cuts from I off the golden standard file to make
                        it compatible with wsj I-length of sentences
    --perc              include the frequencies of each tag in percentage
    --ngr=N             get the N-gram frequencies of each tag (e.g. N=2)
    --amb               allow ambiguous words to be incorporated in analysis

 Misc:
    --version           show program's version number and exit
    -h, --help          show this help message and exit
    -v, --verbose       print status messages in terminal, or debug with -vv

"""

import sys
from docopt import docopt  # install with pip
from os import getcwd
import tagger
import cc


class Ftuk():

    def __init__(self, args):
        """ This is the main wrapper class to carry out functions
         within the program, it basically routs command line parameters
         parsed to the init class from which it will call the appropriate
         classes.

         Just plug stable class dailies in here, don't forget to add args."""

        if args['freq']:
            tagger.main(args)
        elif args['fix']:
            cc.main()
        exit("------- Finished! -------")


def main():
    args = docopt(__doc__, version=__version__)

    if not args['--verbose']:
        f = open(getcwd()+'/outp/log.log', 'w')
        sys.stdout = f

    print " --- FTUK INITIALIZED ---"
    ftuk = Ftuk(args)

if __name__ == '__main__':
    main()