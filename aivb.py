#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 09.02'  # update by date on subclass change
__doc__ = """ AIVB

 Usage:
    aivb mongo load [-a] [--slice=N]
    aivb mongo search --key=k --value=v
    aivb mongo del [-x]
    aivb data [-l] [-s]
    aivb data loop [-e] [-t]
    aivb (-h | --help)
    aivb (-q | --quit)
    aivb --version

 Arguments:
    mongo               used to interface with MongoDB (loading, unloading, etc.)
    data                this executes commands that are directly based on the data
    crunch              this is the evaluation module for the scraped articles

 Mongo:
    load                insert an N amount of articles
    remove              clear the database of all current articles
    -a                  will load the complete dataset, WARNING!
    -x                  display the instances being deleted
    --slice=N           specify the amount of articles you want to use for a test
                        set to soften memory load on dev
    --key=k             key in order to search in MongoDB
    --value=v           value to match the key searching in db

 Data:
    loop
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

class Arguments(dict):

    def store(self, args):
        self.update(args)

class AIVB:

    def __init__(self):
        """ This class is used to call all the required classes
        in core as parent and pass them down to their childs. Can
        be extended if the scraper is also integrated.s """

        self.log = core.logger.Logger()
        self.mongo = core.mongo.Mongo(self.log)
        self.args = Arguments()
        self.boot()

    def boot(self):
        self.args.store(docopt(__doc__, version=__version__))
        wrap = core.wrapper.Wrapper(self.args, self.log, self.mongo)
        wrap.route()


if __name__ == '__main__':
    AIVB()