#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 30.01'  # update by date on subclass change
__doc__ = """ AIVB

 Usage:
    aivb -v eval load [--test=N]
    aivb -v eval data [-l] [-e]
    aivb (-h | --help)
    aivb --version
    aivb (-q | --quit)

 Arguments:
    eval                this is the evaluation module for the scraped articles
    load                loads the results placed in ../res in the working memory,
                        which might take a while to process depending on the size
    data                this executes commands that are directly based on the data

 Load:
    --test=N            specify the amount of articles you want to use for a test
                        set to soften memory load on dev

 Data:
    -l                  get the length of the total dataset
    -e                  get the amount of missing comments

 Misc:
    -h, --help          show this help message and exit
    -v, --verbose       print status messages in terminal, or debug with -vv
    -q, --quit          exit the program, DO IT NAO
    --version           show program's version number and exit

"""

import sys, os
import core
from docopt import docopt  # install with pip


class Wrapper:

    def __init__(self):
        """ This module is used to carry out functions
         within the program, it basically routs command line parameters
         parsed from the init class to the wrapper module from which it
         will call the appropriate classes.

         Just plug stable class dailies in here, don't forget to add args
         to the main class as well. """

        self.obj = None
        self.log = core.logger.Logger()

    def route(self, args):
        outp = {}
        if args['eval']:
            if args['load'] and not self.obj:
                self.obj = core.loader.Loader(args['--test'])
                self.log.elog.info("Database was loaded!")
            else:
                try:
                    if args['-l']:
                        outp.update({'Data size:': self.obj.data_size()})
                    if args['-e']:
                        outp.update({'Empty data:': self.obj.empty_docs()})
                except NameError:
                    self.log.elog.info("Please load the database first.")

        if outp:
            for key, value in outp.iteritems():
                print key + " "*(20-len(key)) + str(value)



def main(store):
    inp = raw_input('>> ').split()
    if inp != 'aivb -q':
        try:
            args = docopt(__doc__, argv=inp[1:], version=__version__)
            if not args['--verbose']:
                sys.stdout = open(os.getcwd()+'/log/log.log', 'w')
            if not store:
                store = Wrapper()
            store.route(args)
            return store
        except (Exception, SystemExit) as e:
            print e
    else:
        raise SystemExit

if __name__ == '__main__':
    store = None; print "Starting AIVB - type: 'aivb -q' to quit & 'aivb -h' for help"
    while True:
        reload(core)
        store = main(store)