#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 06.02'  # update by date on subclass change
__doc__ = """ FTUK!

 Usage:
    ftuk [-v] freq [-srcit] <input>... [--sortk=key] [--top=N] [--perc] [--tex] [--ngr=N] [--amb]
    ftuk [-v] fix <input>
    ftuk [-v] map [-srcit] <input>... [--top=N] [--ttop=N] [--perc] [--tex] [--all]
    ftuk (-h | --help)
    ftuk --version

 Arguments:
    freq                outputs the POS frequencies for one or multiple
                        corpora to terminal or the oupt/res.tex file
    fix                 recompiles the old WSJ corpus to a format usable
                        by ABL, old function, better not use
    map                 create a mapping of the POS tags per likely POS
                        candidate, inherits a lot of code from freq but
                        splitted for better overview
 Freq:
    -s, --sanitize      make sure that GS and STR lists are the same
    -r, --errors        count the errors between GS and STR
    -c, --cor               list the column with correctly learned tags
    -i, --inc               list the column with incorrectly learned tags
    -t, --tot               list the column with the total amount of tags
    --sortk=key         specifically sort the outputted table on key
                        (cor, inc, tot), not specified will sort on tot
    --top=N             output only the top N items
    --perc              include the frequencies of each tag in percentage
    --tex               output in TeX to outp folder, default is print
    --ngr=N             get the N-gram frequencies of each tag (e.g. N=2)
    --amb               allow ambiguous words to be incorporated in analysis

 Map:
    --all               include incorrectly learned tags [INC] in the ouput
    --ttop=N            output only the top N tags

 Misc:
    -h, --help              show this help message and exit
    -v, --verbose           print status messages in terminal, or debug with -vv
    --version           show program's version number and exit

"""

import sys
from docopt import docopt  # install with pip
from os import getcwd
from mods import tagger
from mods import cc
from mods import mapper


class Ftuk:

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
        elif args['map']:
            mapper.main(args)
        exit(" ------- Finished -------")


def main():
    args = docopt(__doc__, version=__version__)

    if not args['--verbose']:
        f = open(getcwd()+'/outp/log.log', 'w')
        sys.stdout = f

    print " --- FTUK INITIALIZED ---"
    ftuk = Ftuk(args)

if __name__ == '__main__':
    main()