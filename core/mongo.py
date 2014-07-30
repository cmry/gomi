#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 27.06'

from core.mapper import TF
from pymongo import Connection
from pymongo.cursor import Cursor
from copy import deepcopy
from glob import glob
from time import strptime, clock
from datetime import datetime
import json
import os
import sys


class Mongo(object):

    def __init__(self, log, sw=None):

        self.name = self.__class__.__name__
        self.log = log
        self.articles = Connection().aivb_db.articles \
            if not sw else Connection().aivb_redux.dater

    def __str__(self):
        return """
                'all':        None,
                'search':     {k: v},
                'empty':      {k: 0},
                'filled':     {k: {'$gt': 0.5}},
                'gtv':        {k: {'$gt': v}},
                'regex':      {k: {'$regex': v}},
                'exists':     {k: {'$exists': True}},
                'and_ex':     {'$and': [{k: v}, {k2: {'$exists': True}}]},
                'grt_ex':     {'$and': [{k: {'$exists': True}}, {k2: {'$gt': v2}}]},
                'grt_eq':     {'$and': [{k: {'$exists': True}}, {k2: v2}]},
                'p_range':    {'$and': [{k: {'$gte': v}}, {k2: {'$lte': v2}}]},
                'period':     {'$and': [{k: v}, {k2: {'$gt': v2}}]},
                'andand':     {'$and': [{k: v}, {k2: v2}]}
                """

    def load(self, n=None):
        load = Loader(self.log)
        data = load.fetch_data(n)
        [[self.articles.insert(i) for i in x] for x in data]
        self.log.mlog.info("Inserted %d Instances of articles." % n)

    def search(self, command, key=None, value=None, s_key=None, s_value=None, t_key=None):
        if not key:
            res = [self.articles.find_one()]
        else:
            res = self.parse_search(command, key, value, s_key, s_value, t_key)
        return res

    def clear_all(self, v=None):
        for art in self.articles.find():
            if v:
                print art
            self.articles.remove(art)

    def parse_search(self, c, k, v, k2, v2, k3):
        op = {'all':        None,
              'search':     {k: v},
              'empty':      {k: 0},
              'filled':     {k: {'$gt': 0.5}},
              'gtv':        {k: {'$gt': v}},
              'regex':      {k: {'$regex': v}},
              'exists':     {k: {'$exists': True}},
              'and_ex':     {'$and': [{k: v}, {k2: {'$exists': True}}]},
              'grt_ex':     {'$and': [{k: {'$exists': True}}, {k2: {'$gt': v2}}]},
              'grt_eq':     {'$and': [{k: {'$exists': True}}, {k2: v2}]},
              'p_range':    {'$and': [{k: {'$gte': v}}, {k2: {'$lte': v2}}]},
              'period':     {'$and': [{k: v}, {k2: {'$gt': v2}}]},
              'andand':     {'$and': [{k: v}, {k2: v2}]}
              }
        if 'select' not in c:
            return self.articles.find(op[c])
        else:
            if not k3:
                return self.articles.find(op[c.split('_')[1]], {'_id': k2, v2: 1})
            else:
                return self.articles.find(op[c.split('_')[1]], {'_id': k2, v2: 1, k3: 1})

    def update(self, c, eid, k, v, k2=None):
        op = {'one':        {'$set': {k: v}},
              'two':        {'$set': {k2: {'$set': {k: v}}}}
              }
        self.articles.update({'_id': eid}, op[c], upsert=False, multi=False)


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

        rng = [int(x) for x in str(args['--lrange']).split('-')] if args['--lrange'] else None
        if args['-l']:
            self.data_size()
        if args['-e']:
            self.count_docs()
        if args['-m']:
            self.miss_docs()
        if args['-o']:
            self.commentc()
        if args['-r']:
            self.articlec()
        if args['--scope']:
            if args['--scope'] == 'topics':
                self.topics(rng)
            elif args['--scope'] == 'comments':
                self.r_comments(rng)
            elif args['--scope'] == 'articles':
                self.r_articles(rng)

    def data_size(self):
        """ Return the size of the data for confirmation. """
        self.output.append("Data size: %d" % self.articles.count())

    def count_docs(self):
        """ Count the amount of populated docs. """
        self.output.append("Populated: %d" % Cursor.count(self.search('filled', 'cmt_count')))

    def miss_docs(self):
        self.output.append("Missing: %d" % Cursor.count(self.search('empty', 'cmt_count')))

    def articlec(self):
        self.output.append("Article Amount: %d" % Cursor.count(self.search('exists', 'nr')))

    def commentc(self):
        self.output.append("Comment Amount: %d" % Cursor.count(self.search('exists', 'comment_id')))

    def r_articles(self, rng):
        self.output.append("Article Amount: %d" % Cursor.count(
            self.search('select_gtv', 'date', datetime(rng[0], rng[1], 1), 0, 'nr')))

    def r_comments(self, rng):
        self.output.append("Comment Amount: %d" % Cursor.count(
            self.search('select_gtv', 'comment_date', datetime(rng[0], rng[1], 1), 0, 'comment_id')))

    def topics(self, rng):
        x = self.search('select_gtv', 'date', datetime(rng[0], rng[1], 1), 0, 'subjects')
        tl = []
        [[tl.append(j) for j in i['subjects'].split(', ')] for i in x]
        self.output.append("Topic Amount: %d" % len(set(tl)))
        # self.output.append("Topic top: \n" + str(TF.get_freq(tl).most_common(100)))
        self.output.append("Topic select: %d" % len([x for x in TF.get_freq(tl).most_common() if x[1] > 2]))


class Loader(Mongo):

    com_count = 0
    tot_time = []

    @staticmethod
    def fetch_done():
        os.chdir(os.getcwd()+'/res/')
        d = glob('*.txt')
        os.chdir(os.getcwd()+'/../')
        return d

    def fetch_data(self, n=None):
        """ This generator opens all the files up to n given
         sample size, requires n to be an int, check was removed.
         Default opens all the files. Parses and inserts. """

        res, done = self.fetch_done(), [str(x['id'])+'.txt' for x in self.search('filled', 'id')]
        do = list(set(res).symmetric_difference(set(done)))

        if not n:
            n = len(do)
        data, n, t = [], n, n

        for fl in do:
            t1 = clock()
            if n < 1:
                print "\n"; break
            with open(os.getcwd()+"/res/"+fl, 'r') as f:
                try:
                    yield [x for x in self.__parse_jfile(f)]
                except ValueError:
                    self.log.llog.warning("JSON file " + str(f) + " was not recognized!")
            n -= 1
            self.tot_time.append((clock()-t1)/2)
            self.__perc(n, t, reduce(lambda x, y: x + y, self.tot_time) / len(self.tot_time))

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
                # add identifier stuff to comments
                cmt = self.__parse_date(cmt, 'comment_')
                cmt['comment_art'] = doc['id']
                cmt['comment_source'] = doc['source']
                cmt['comment_topic'] = doc['subjects']
                cmt['comment_title'] = doc['content']['title']
                self.com_count += 1; local_count += 1
                yield cmt_list
        doc['cmt_count'] = local_count
        yield doc

    def __parse_date(self, jdoc, prep=''):
        """ Preprocess datestamps into date format. """
        date, brk = [x.lower() for x in jdoc[prep+'date'].split()], False
        try:
            int(date[0])
        except ValueError:
            date = [x for x in reversed(date)]
        except IndexError:
            jdoc[prep+'date'] = datetime(*strptime('1 3 1937 13:37', '%d %m %Y %H:%M')[:6]); brk = True
        if not brk:
            try:
                jdoc[prep+'date'] = datetime(*strptime(str(int(date[0])) + " " + self.__parse_month(date[1]) + " " +
                                                       jdoc[prep+'year'] + " " + jdoc[prep+'time'], '%d %m %Y %H:%M')[:6])
            except IndexError:
                jdoc[prep+'date'] = datetime(*strptime('1 3 1937 13:37', '%d %m %Y %H:%M')[:6])

        del jdoc[prep+'year']; del jdoc[prep+'time']; return jdoc

    def __parse_month(self, date):
        datel = {
            'januari':      '1',
            'january':      '1',
            'februari':     '2',
            'february':     '2',
            'maart':        '3',
            'march':        '3',
            'april':        '4',
            'mei':          '5',
            'may':          '5',
            'juni':         '6',
            'june':         '6',
            'juli':         '7',
            'july':         '7',
            'augustus':     '8',
            'august':       '8',
            'september':    '9',
            'oktober':      '10',
            'october':      '10',
            'november':     '11',
            'december':     '12'
        }
        return datel[date.lower()]

    def __perc(self, curr, tot, time):
        """ Small function to display percentage of total for
        decreasing range. """
        print >> sys.stdout, "\r%d%% \t ETA: %f" % (int(float(100)-(float(curr)/float(tot)*100)), ((time*curr)/60.0/60.0)),
        sys.stdout.flush()