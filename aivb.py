#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 05.02'  # update by date on subclass change
__doc__ = """ AIVB

 Usage:
    aivb load [--slice=N]
    aivb data [-l] [-s] [--loop] [-e] [-t]
    aivb (-h | --help)
    aivb (-q | --quit)
    aivb --version

 Arguments:
    crunch              this is the evaluation module for the scraped articles
    load                loads the results placed in ../res in the working memory,
                        which might take a while to process depending on the size
    data                this executes commands that are directly based on the data

 Load:
    --loop              wrap actions that need a loop to process (-e)
    --slice=N            specify the amount of articles you want to use for a test
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

import core
from docopt import docopt  # install with pip


class AIVB:

    def __init__(self):

        self.log = core.logger.Logger()
        self.data = None
        self.args = None
        while True:
            self.boot_env()

    def boot_env(self):

        self.reload_mods('all')
        inp = raw_input('>> ').split()

        if inp != '-q':
            try:
                self.args = docopt(__doc__, argv=inp, version=__version__)
                # this part handles loading the database with n sample size
                if self.args['load'] and not self.data:
                    self.call_loader(self)
                # if loaded, call the wrapper
                elif self.data:
                    self.wrap_args()
                # else yield waring
                else:
                    self.log.elog.warning("Please load the database first.")
            except (Exception, SystemExit):
                self.log.elog.exception("Error: ")
        else:
            raise SystemExit

    def reload_mods(self, target):
        if target == 'all':
            reload(core)

    def call_loader(self, args):
        load = core.loader.Loader()
        self.data = load.fetch_data(args['--slice'])

    def wrap_args(self):
        wrap = core.wrapper.Wrapper()
        wrap.route()

if __name__ == '__main__':
    print "Starting AIVB - type: '-q' to quit & '-h' for help"
    AIVB()