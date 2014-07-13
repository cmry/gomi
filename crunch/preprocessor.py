#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 03.07'

from pymongo import Connection
from core.mongo import Mongo
from core.mapper import TF
from re import sub
from datetime import datetime
from HTMLParser import HTMLParser
from os import chdir, getcwd
from csv import writer


class Preprocess(Mongo):

    output = []

    def __str__(self):
        if self.output:
            outp = [str(x).replace(': ', (':'+' '*(40-len(x)))) for x in self.output]
            return '\n'.join(outp)
        else:
            self.log.plog.error("There was no output to display!")
            return ""

    # TODO: check all route args if they do not exclude eachother with elifs
    def route_args(self, args):
        if args['label']:
            if args['--dater']:
                self.label_dates(args['--dater'])
            elif args['--subjr']:
                self.label_subj(args['--subjr'])
            elif args['--perir']:
                self.label_period()
        if args['dump']:
            if args['--outp']:
                self.dump_db(args)
            elif args['--split']:
                self.split()

    def timer(self, t1, label):
        td = datetime.now()-t1
        self.output.append('Message: '+'%s relabelled!' % label)
        self.output.append('Time: '+str(td.seconds//60)+'m '+str(td.seconds)+'s')

    def update_date(self, date, prep=''):
        art_l = [x for x in self.search('select_exists', prep+'date', None, 1, prep+'date')]
        [self.update('one', art_l[i]['_id'], 'date_range',
                     False if art_l[i][prep+'date'] < date else True) for i in range(0, len(art_l))]

    def label_dates(self, r):
        r, t1 = [int(x) for x in r.split('-')], datetime.now()
        date = datetime(r[0], r[1], 1)
        self.update_date(date, 'comment_'); self.update_date(date)
        self.timer(t1, 'dates')

    def get_subj(self, prep, k3=None):
        return [x for x in self.search('select_exists', prep, None, 1, prep, k3)]

    def label_subj(self, r):
        fldl, t1 = ['comment_topic', 'subjects'], datetime.now()
        art_l, tl = self.get_subj('subjects', 'date_range'), []
        [[tl.append(j) for j in i['subjects'].split(', ')] if i['date_range'] else [] for i in art_l]
        tf_l = TF.get_freq(tl)
        for fl in fldl:
            art_l = self.get_subj(fl)
            for i in range(0, len(art_l)):
                n_tl, i_tl = [], art_l[i][fl].split(', ')
                [n_tl.append(t) if tf_l[t] >= int(r) else None for t in i_tl]
                self.update('one', art_l[i]['_id'], 'subject_range', ', '.join(n_tl))
                self.update('one', art_l[i]['_id'], 'subject_count', len(n_tl))
        self.timer(t1, 'subjects')

    def update_period(self, perd, prep):
        art_l = [x for x in self.search('select_exists', prep+'date', None, 1, prep+'date')]

        for i in range(0, len(art_l)):
            for k in perd.iterkeys():
                label = 'NaP'
                if perd[k][0] <= art_l[i][prep+'date'] <= perd[k][1]:
                    label = k; break
            self.update('one', art_l[i]['_id'], 'period_label', label)

    def label_period(self):
        t1 = datetime.now()
        perd = {'ESP': [datetime(2013, 01, 01), datetime(2013, 06, 30)],
                'SP':  [datetime(2013, 07, 01), datetime(2013, 12, 31)],
                'OSP': [datetime(2014, 01, 01), datetime(2014, 06, 30)]}
        [self.update_period(perd, i) for i in ['', 'comment_']]
        self.timer(t1, 'periods')

    def dump_db(self, args):

        prep = args['--outp']+'_' if args['--outp'] == 'comment' else ''
        out_cursor = self.search('grt_eq', prep+'date', None, 'date_range', True)

        if not args['--switch']:
            args['--switch'] = 'nu.nl tweakers.net'
            pop = 'all'
        else:
            pop = args['--switch'].split('.')[0]

        chdir(getcwd()+'/outp')
        with open(args['--outp']+'_'+pop+'_ti.csv', 'wb') as fp:
            cw = writer(fp, delimiter=',', quotechar='"')
            cw.writerows(self.extract_data(out_cursor, prep, args['--switch']))
        chdir(getcwd()+'/../crunch')

    def extract_data(self, d, prep, sw, data=list(), i=0):
        for x in d:
            _id, source, date, per = x['_id'], x[prep+'source'], x[prep+'date'], x['period_label']
            if x['subject_range'] and source in sw:
                i += 1                                          # hotfix for double topics
                tags = ' '.join([y.replace(' ', '_') for y in list(set(x['subject_range'].split(', ')))])
                try:
                    title = self.sanitize(x['content']['title'])
                    text = title + '. ' + self.sanitize(x['content']['text'] if 'intro' not in x['content'] else x['content']['intro'] + ' ' + x['content']['text'])
                except KeyError:
                    title = self.sanitize(x[prep+'title'])
                    text = self.sanitize(x[prep+'text'])
                data.append([str(i), _id, source, date, per]+[x.encode("utf-8") for x in [tags, title, text]])
        return data

    def split(self):
        newc = Connection().aivb_redux.dater
        [newc.insert(x) for x in self.search('period', 'date_range', True, 'subject_count', 1)]
        self.log.mlog.info("New database was created!")

    def sanitize(self, text):
        text = text.replace('\t', ' ').replace('\n', ' ')
        text = ' '.join([self.strip_tags(x) if '<' in x else x for x in text.split()])
        text = sub('[A-Z]+ - ', '', text)
        return text

    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)