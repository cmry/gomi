#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 05.02'

from pymongo import Connection
import json
import os
import sys

class Mongo:

    def __init__(self, log):

        self.log = log

        con = Connection()
        db = con.aivb_db
        self.articles = db.articles

    def insert_db(self, obj):
        self.articles.insert(obj)

    def populate_db(self, dict):
        for art in dict:
            self.articles.insert(art)

    # TODO: merge these into one function
    def grab_all(self):
        res = self.articles.find()
        for art in res:
            print art

    def grab_one(self):
        return self.articles.find_one()

    def grab_row(self, key, value):
        print key, value
        res = self.articles.find({key: value})
        for art in res:
            print art

    def grab_regex(self, key, pattern):
        res = self.articles.find({key: {'$regex': pattern}})
        for art in res:
            print art

    def clear_all(self, v=None):
        for art in self.articles.find():
            if v:
                print art
            self.articles.remove(art)

    def fetch_data(self, n, halt):
        """ This generator opens all the files up to n given
         sample size, requires n to be an int, check was removed.
         default opens all the files. """

        if n is 0:
            n = len([name for name in os.listdir(os.getcwd()+"/res") if os.path.isfile(name)])
        data, n, t = [], n, n

        # as long as we're in the slice range, get files
        for fl in os.listdir(os.getcwd()+"/res"):
            self.perc(n, t)
            if n < 1 and halt: print "\n"; break
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

    def perc(self, curr, tot):
        """ Small function to display percentage of total for
        decreasing range. """
        print >> sys.stdout, "\r%d%%" % (int(float(100)-(float(curr)/float(tot)*100))),
        sys.stdout.flush()
