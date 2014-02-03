#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 03.02'  # update by date on subclass change
__doc__ = """ AIVB

 Usage:
    aivb load [--test=N]
    aivb data [-l] [-s] [--loop] [-e] [-t]
    aivb (-h | --help)
    aivb (-q | --quit)
    aivb --version

 Arguments:
    eval                this is the evaluation module for the scraped articles
    load                loads the results placed in ../res in the working memory,
                        which might take a while to process depending on the size
    data                this executes commands that are directly based on the data

 Load:
    --loop              wrap actions that need a loop to process (-e)
    --test=N            specify the amount of articles you want to use for a test
                        set to soften memory load on dev

 Data:
    -l                  get the length of the total dataset
    -e                  get the amount of missing comments
    -s                  print sample of the output
    -t                  print the list of different dates

 Misc:
    -h, --help          show this help message and exit
    -v, --verbose       print status messages in terminal, or debug with -vv
    -q, --quit          exit the program, DO IT NAO
    --version           show program's version number and exit

"""

import sys, os
import core
from docopt import docopt  # install with pip
from traceback import print_tb


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
        """ The route functions handles the arguments and pipes them to
        the appropriate functions. """
        outp = {}

        # this part handles loading the database with n sample size
        if args['load'] and not self.obj:
            self.obj = core.loader.Loader(args)
            self.log.elog.info("Database was loaded!")

        # this part wraps actions that are carried out directly on the
        # sample set without extensive functions
        elif args['data'] and self.obj:
                if args['--loop']:
                    dic = self.obj.data_wrapper(args)
                    outp.update(dic)
                else:
                    if args['-l']:
                        outp.update({'Data size:': self.obj.data_size()})
                    if args['-s']:
                        outp.update({'Data sample:': self.obj.sample()})
        else:
            self.log.elog.info("Please load the database first.")

        # if there's any output to display, do so
        if outp:
            for key, value in outp.iteritems():
                print key + " "*(20-len(key)) + str(value)



def main(store):
    inp = raw_input('>> ').split()
    if inp != '-q':
        try:
            # TODO: the data object gets lost if a help function is called
            args = docopt(__doc__, argv=inp, version=__version__)
            #if not args['--verbose']:
            #    sys.stdout = open(os.getcwd()+'/log/log.log', 'w')
            if not store:
                store = Wrapper()
            store.route(args)
            return store
        except (Exception, SystemExit) as e:
            print "Error: "+str(e)

    else:
        raise SystemExit

if __name__ == '__main__':
    store = None; print "Starting AIVB - type: '-q' to quit & '-h' for help"
    while True:
        reload(core)
        store = main(store)