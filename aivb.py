#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 09.02'  # update by date on subclass change
__doc__ = """ AIVB

 Usage:
    aivb mongo load [-a] [--slice=N]
    aivb mongo search [--key=k] [--value=v]
    aivb mongo del [-x]
    aivb lookup [-lem]
    aivb (-h | --help)
    aivb (-q | --quit)
    aivb --version

 Arguments:
    mongo               used to interface with MongoDB (loading, unloading, etc.)
    lookup              this executes commands to directly display data info
    crunch              this is the evaluation module for the scraped articles

 Mongo:
    load                insert an N amount of articles
    -a                  will load the complete dataset, WARNING!
    --slice=N           specify the amount of articles you want to use for a test
                        set to soften memory load on dev

    search              used to quickly debug the MongoDB content
    --key=k             key in order to search in MongoDB
    --value=v           value to match the key searching in db

    del                 clear the database of all current articles
    -x                  display the instances being deleted

 Lookup:
    -l                  get the length of the total dataset
    -e                  get the amount of existing comments
    -m                  get the amount of missing comments

 Misc:
    -h, --help          show this help message and exit
    -v, --verbose       print status messages in terminal, or debug with -vv
    --version           show program's version number and exit

"""

from core.mongo import Mongo, Lookup
from core.logger import Logger
from docopt import docopt  # install with pip

class AIVB:

    def __init__(self):
        """ This class is used to call all the required classes
        in core as parent and pass them down to their childs. Can
        be extended if the scraper is also integrated.s """

        try:
            self.log = Logger()
            self.args = docopt(__doc__, version=__version__)
            self.__dispatch()
        except Exception:
            self.log.elog.exception("Error: ")

    def __dispatch(self):
        """ This module is used to carry out functions
         within the program, it basically routs command line parameters
         parsed from the init class to the wrapper module from which it
         will call the appropriate classes.

         Just plug stable class dailies in here, don't forget to add self.args
         to the main class as well. """

        if self.args['mongo']:
            self.__route_mongo()
        elif self.args['lookup']:
            self.__route_lookup()


    def __route_mongo(self):
        args, db = self.args, Mongo(self.log)
        if args['load'] and args['-a']:
            db.load()
        elif args['load'] and args['--slice']:
            db.load(int(args['--slice']))
        elif args['search']:
            print "Output: %s" % [x for x in db.search(args['--key'], args['--value'])]
        elif args['del']:
            db.clear_all(True if args['-x'] else False)

    def __route_lookup(self):
        args, db = self.args, Lookup(self.log)
        db.route_args(args)
        print(db)


if __name__ == '__main__':
    AIVB()