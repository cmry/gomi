#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 03.07'  # update by date on subclass change
__doc__ = """ AIVB

 Usage:
    aivb scrape (-t | -n) --min=n --max=x --intv=i [--check] [--radar]
    aivb mongo load [-a] [--slice=N]
    aivb mongo [z] (search | retr) [--key=k] [--value=v]
    aivb mongo [z] del [-x]
    aivb lookup [z] [-lemro] [--scope=sc] [--lrange=lr]
    aivb prep [z] label [(--dater=dr | --subjr=sr | --perir)]
    aivb prep [z] dump [--switch=sw] [--outp=op] [--split]
    aivb grapher [z] [-c] (--dates | --topics) [--style=s] [(--months | --years)] [--range=r]
    aivb classifier [--kf=kf] --train=tr --test=te --mem=mem --mod=ml
    aivb logger --comp
    aivb (-h | --help)
    aivb (-q | --quit)
    aivb --version

 Arguments:
    scrape              scraper for Nu.nl and Tweakers.net to fill the dataset
    mongo               used to interface with MongoDB (loading, unloading, etc)
    lookup              this executes commands to directly display data info
    prep                used to preprocess the existing db entries
    grapher             is used to display statistics in a nice graph
    classifier          the classifier implements tenfold cross-validation and a
                        bootstrap for the Stanford Topic Modelling Toolbox (STMT)
    logger              operates on the dumped dataset from preprocessing
    z                   z reduces the dataset to predefined ranges stated in
                        the preprocessing module, requires split

 Scrape:
    -t                  scrape n-x with interval i from Tweakers.net
    -n                  scrape n-x with interval i from Nu.nl
    --min=m             starting amount of article numbers
    --max=x             ending amount of article numbers
    --intv=i            time interval between page queries
    --check             check if already in log
    --radar             do some stealthy stuff

 Mongo:
    load                insert an N amount of articles
    -a                  will load the complete dataset, WARNING!
    --slice=N           specify the amount of articles to use for a test
                        set to soften memory load on dev

    search              used to quickly debug the MongoDB content
    retr                only show value field from entries that have key
    --key=k             key in order to search in MongoDB
    --value=v           value to match the key searching in db

    del                 clear the database of all current articles
    -x                  display the instances being deleted

 Lookup:
    -l                  get the length of the total dataset
    -e                  get the amount of existing comments
    -m                  get the amount of missing comments
    -r                  get the total amount of articles
    -o                  get the total amount of comments
    --scope=sc          get a more scoped view on the dataset
                        where sc can be 'topics', 'comments' and
                        'articles'.
    --lrange=lr         from a certain date range (year-month)

 Prep:
    label               for applying new lables to existing dataset
    --dater=dr          will label all articles and comments that are
                        older than the specified datetime dr with
                        date_range = True, else it will be set to False.
    --subjr=sr          labels all articles that have subjects that are
                        more frequent than the specified tr with only
                        these subjects, leaving out less frequent ones
    --perir             applies a label for each comment or article when
                        it falls in the PSP, SP, or OSP (thesis specific).

    dump                for moving stuff around
    --switch=sw         sw can be either True to include 1 topic ouput,
                        creating a purely Bayesian machinery, with True
                        it is more usefull for topic models.
    --outp=op           op can be either 'comment' or 'article'
    --split             reduces the dataset to allow z

 Grapher:
    -c, --comments      include comments
    --dates             export the date graph
    --topics            export the comment graph
    --style=s           graph style (bar)
    --years             split sources on years
    --months            split sources on months
    --range=r           from a certain date range (year-month)st

 Classifier:
    --kf=kf             if train and test are equal sets, loops k
                        slices as training set, default is ten
    --train=tr          input the set you want to train on
    --test=te           input the set you want to test on
    --mem=mem           amount of used memory (1000 or 8000 f.e.)
    --mod=ml            desired model to run, lda or llda, should
                        be same name as the scala scripts to run STMT

 Logger:
    --comp              compresses the log in one file

 Misc:
    -h, --help          show this help message and exit
    -v, --verbose       print status messages in terminal, or debug with -vv
    --version           show program's version number and exit

"""

from scraper.scraper import Scraper
from core.mongo import Mongo, Lookup
from core.logger import Logger
from crunch.grapher import Grapher
from crunch.preprocesser import Preprocess
from crunch.classifier import Classifier
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
         within the program, it basically routes command line parameters
         parsed from the init class to the wrapper module from which it
         will call the appropriate classes.

         Just plug stable class dailies in here, don't forget to add self.args
         to the main class as well. """

        sw = None if not self.args['z'] else 'sw'

        if self.args['scrape']:
            self.__route_scraper()
        elif self.args['mongo']:
            self.__route_mongo(sw)
        elif self.args['lookup']:
            self.__route_mod(Lookup(self.log, sw))
        elif self.args['prep']:
            self.__route_mod(Preprocess(self.log, sw))
        elif self.args['grapher']:
            self.__route_mod(Grapher(self.log, sw))
        elif self.args['classifier']:
            self.__route_mod(Classifier(self.log))
        elif self.args['logger']:
            self.__route_mod(Logger())

    def __route_scraper(self):
        args = self.args
        sc = Scraper(int(args['--min']),
                     int(args['--max']),
                     't' if args['-t'] else 'n',
                     int(args['--intv']),
                     'true' if not args['--check'] else None,
                     'true',
                     self.log)

    def __route_mongo(self, sw):
        args, db = self.args, Mongo(self.log, sw)
        if args['load'] and args['-a']:
            db.load()
        elif args['load'] and args['--slice']:
            db.load(int(args['--slice']))
        elif args['search']:
            print "Output: %s" % [x for x in db.search('search', args['--key'], args['--value'])]
        elif args['retr']:
            print "Output: %s" % [x for x in db.search('select_exists', args['--key'], None, args['--value'], None)]
        elif args['del']:
            db.clear_all(True if args['-x'] else False)

    def __route_mod(self, mod):
        mod.route_args(self.args)
        print mod


if __name__ == '__main__':
    AIVB()