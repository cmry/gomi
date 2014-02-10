#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 10.02'

from pymongo import Connection
from pymongo.cursor import Cursor
from copy import deepcopy
from time import strptime
from datetime import datetime
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
        [[self.articles.insert(i) for i in x] for x in load.fetch_data(n)]
        self.log.mlog.info("Inserted %d Instances of articles." % n)

    def search(self, command, key=None, value=None, l_key=None):
        if not key:
            res = [self.articles.find_one()]
        else:
            res = self.parse_search(command, key, value)
        return res

    def clear_all(self, v=None):
        for art in self.articles.find():
            if v:
                print art
            self.articles.remove(art)

    def parse_search(self, c, k, v):
        op = {'all':        None,
              'search':       {k: v},
              'filled':     {k: {'$gt': 0.5}},
              'empty':      {k: 0},
              'regex':      {k: {'$regex': v}},
              'exists':       {k: {'$exists': True}}
              }
        return self.articles.find(op[c])


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
        if args['-c']:
            self.comments()

    def data_size(self):
        """ Return the size of the data for confirmation. """
        self.output.append("Data size: %d" % self.articles.count())

    def count_docs(self):
        """ Count the amount of populated docs. """
        self.output.append("Populated: %d" % Cursor.count(self.search('filled', 'cmt_count')))

    def miss_docs(self):
        self.output.append("Missing: %d" % Cursor.count(self.search('empty', 'cmt_count')))

    def comments(self):
        self.output.append("Comment Amount: %d" % Cursor.count(self.search('exists', 'comment_id')))


class Loader(Mongo):

    com_count = 0

    def fetch_data(self, n=None):
        """ This generator opens all the files up to n given
         sample size, requires n to be an int, check was removed.
         Default opens all the files. Parses and inserts. """

        data, n, t, = [], n, n
        if not n:
            n = len([name for name in os.listdir(os.getcwd()+"/res") if os.path.isfile(name)])

        # as long as we're in the slice range, get files
        for fl in os.listdir(os.getcwd()+"/res"):
            if n < 1:
                print "\n"
                break
            if fl.endswith(".txt"):  # avoid litter
                with open(os.getcwd()+"/res/"+fl, 'r') as f:
                    try:
                        yield [x for x in self.__parse_jfile(f)]
                    except ValueError:  # this might be unnecessary
                        self.log.llog.warning("JSON file " + str(f) + " was not recognized!")
                n -= 1
            else:
                self.log.llog.warning("A non .txt was detected!")
            self.__perc(n, t)

        self.log.llog.info("Database was loaded!")
        self.log.llog.info("Inserted %d instances of comments." % self.com_count)

    def __parse_jfile(self, f):
        """ Fix all the dump from our JSON files for BSON."""
        jf, local_count = json.load(f), 0
        # per article, strip contents and split comments
        doc = deepcopy(self.__parse_date(jf))
        cmt_list = doc.pop('comments')

        if cmt_list:
            for cmt in cmt_list:
                cmt = self.__parse_date(cmt, 'comment_')
                cmt['comment_art'] = doc['id']
                self.com_count += 1; local_count += 1
                yield cmt_list
        doc['cmt_count'] = local_count
        yield doc

    def __parse_date(self, jdoc, prep=str()):
        """ Preprocess datestamps into date format. """
        date = [x.lower() for x in jdoc[prep+'date'].split()]
        try:
            int(date[0])
        except ValueError:
            date = [x for x in reversed(date)]
        try:
            jdoc[prep+'date'] = datetime(*strptime(str(int(date[0])) + " " + self.__parse_month(date[1]) + " " +
                                                   jdoc[prep+'year'] + " " + jdoc[prep+'time'], '%d %m %Y %H:%M')[:6])
        except IndexError:
            jdoc[prep+'date'] = 'UNK'

        del jdoc[prep+'year']; del jdoc[prep+'time']; return jdoc

    def __parse_month(self, date):
        datel = {
            'januari':      '1',
            'februari':     '2',
            'maart':        '3',
            'april':        '4',
            'mei':          '5',
            'juni':         '6',
            'juli':         '7',
            'augustus':     '8',
            'september':    '9',
            'oktober':      '10',
            'november':     '11',
            'december':     '12'
        }
        return datel[date.lower()]

    def __perc(self, curr, tot):
        """ Small function to display percentage of total for
        decreasing range. """
        print >> sys.stdout, "\r%d%%" % (int(float(100)-(float(curr)/float(tot)*100))),
        sys.stdout.flush()