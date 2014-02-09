#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 05.02'

from pymongo import Connection
from pymongo.cursor import Cursor
from copy import deepcopy
import json
import os
import sys


class Mongo(object):

    def __init__(self, log):

        self.name = self.__class__.__name__
        self.log = log
        self.articles = Connection().aivb_db.articles

    def load(self, n=None):
        load = Loader(self.log)
        [self.articles.insert(x) for x in load.fetch_data(n)]
        self.log.mlog.info("Inserted %d amount of articles." % n)

    def search(self, key=None, value=None):
        if not key:
            res = self.articles.find_one()
        else:
            if key == 'all':
                res = self.articles.find()
            elif key == 'filled':
                res = self.articles.find({value: {'$not': {'$size': 0}}})
            elif key == 'empty':
                res = self.articles.find({value: {'$size': 0}})
            elif 'r=' in value:
                # TODO: fix
                pattern = value.split('=')[1]
                res = self.articles.find({key: {'$regex': pattern}})
            else:
                res = self.articles.find({key: value})
        return res

    def clear_all(self, v=None):
        for art in self.articles.find():
            if v:
                print art
            self.articles.remove(art)


class Loader(Mongo):

    def fetch_data(self, n=None):
        """ This generator opens all the files up to n given
         sample size, requires n to be an int, check was removed.
         default opens all the files. """

        if not n:
            n = len([name for name in os.listdir(os.getcwd()+"/res") if os.path.isfile(name)])
        data, n, t = [], n, n

        # as long as we're in the slice range, get files
        for fl in os.listdir(os.getcwd()+"/res"):
            self.__perc(n, t)
            if n < 1: print "\n"; break
            if fl.endswith(".txt"):  # avoid litter
                with open(os.getcwd()+"/res/"+fl, 'r') as f:
                    try:
                        jf = json.load(f)
                        yield jf
                    except ValueError:  # this might be unnecessary
                        self.log.llog.warning("JSON file " + str(f) + " was not recognized!")
                n -= 1
            else:
                self.log.llog.warning("A non .txt was detected!")
        self.log.llog.info("Database was loaded!")

    def __perc(self, curr, tot):
        """ Small function to display percentage of total for
        decreasing range. """
        print >> sys.stdout, "\r%d%%" % (int(float(100)-(float(curr)/float(tot)*100))),
        sys.stdout.flush()

class Lookup(Mongo):

    output = []
    sec_loop = False  # required to omit the second loop by choice

    def __str__(self):
        if self.output:
            outp = [str(x).replace(': ', (':'+' '*(25-len(x)))) for x in self.output]
            return '\n'.join(outp)
        else:
            self.log.lolog.error("There was no output to display!")
            return ""

    def route_args(self, args):
        """ Routes passed arguments to the appropriate mongo
        functions. """

        if args['-l']:
            self.data_size()
        if args['-e']:
            self.count_docs()
        if args['-m']:
            self.miss_docs()

    def data_size(self):
        """ Return the size of the data for confirmation. """
        self.output.append("Data size: %d" % self.articles.count())

    def count_docs(self):
        """ Count the amount of populated docs. """
        self.output.append("Populated: %d" % Cursor.count(self.search('filled', 'comments')))

    def miss_docs(self):
        self.output.append("Missing: %d" % Cursor.count(self.search('empty', 'comments')))