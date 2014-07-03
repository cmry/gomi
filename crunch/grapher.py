#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 20.06'

from core.mongo import Mongo
from core.mapper import TF
from heapq import merge
from collections import OrderedDict
from pandas import *
import pygal
import matplotlib
import matplotlib.pyplot as plt
import datetime


class Grapher(Mongo):

    args = None

    def route_args(self, args):
        self.args = args
        if args['--dates']:
            self.__date_chart()
        if args['--topics']:
            self.__topic_plot() #  self.__topic_chart()

    def __fetch_period(self, stack, needle, conf, period, dt):
        res = [x[conf].year
               if period != 'months'
               else str(x[conf].year)+'-'+(str(x[conf].month) if int(x[conf].month) > 9 else '0'+str(x[conf].month))
               for x in self.search('search' if not dt else 'period', stack, needle, conf, dt)]
        res.sort()
        return res

    @staticmethod
    def get_freq(s, comb):
        scomb, l = set(comb), [dict() for _ in range(0, 4)]
        for x in scomb:
            for y in range(0, len(l)):
                l[y][x] = 0
        for x in range(0, len(s)):
            for y in s[x]:
                l[x][y] += 1
        return l, scomb

    def __sort_input(self, s, d=[]):
        l, scomb = self.get_freq(s, list(merge(s[0], s[1], s[2], s[3])))
        for x in l:
            d.append(OrderedDict(sorted(x.items(), key=lambda t: t[0])))
        return [d[0], d[2], d[1], d[3]], scomb

    def __fetchem(self, period, dt):
        l = [[], [], [], []]
        l[0] = self.__fetch_period('source', 'tweakers.net', 'date', period, dt)
        l[1] = self.__fetch_period('source', 'nu.nl', 'date', period, dt)
        if self.args['-c']:
            l[2] = self.__fetch_period('comment_source', 'tweakers.net', 'comment_date', period, dt)
            l[3] = self.__fetch_period('comment_source', 'nu.nl', 'comment_date', period, dt)
        return l

    def __graph(self, p):
        if self.args['--style'] == 'bar':
            return pygal.Bar(logarithmic=True if 'log' in p else False)  # , style=pygal.style.LightColorizedStyle)
        if self.args['--style'] == 'line':
            return pygal.StackedLine(logarithmic=True if 'log' in p else False, x_label_rotation=30)
        else:
            exit("Ye focked it.")

    def __fetch_range(self):
        if self.args['--range']:
            rng = self.args['--range'].split('-')
            dt = datetime.datetime(int(rng[0]), int(rng[1]), 1)
            return dt
        else:
            return None

    def __date_chart(self):

        dt = self.__fetch_range()

        d, scomb = self.__sort_input([x for x in self.__fetchem('months' if self.args['--months'] else False, dt)])
        f = ['T.net Articles', 'T.net Comments', 'Nu.nl Articles', 'Nu.nl Comments']

        g = self.__graph('log')
        g.title = 'Document frequency'
        g.x_labels = [str(k) for k in sorted(scomb)]

        for i in range(0, len(f)):
            if not self.args['-c'] and 'Comments' in f[i]: pass
            else: g.add(f[i], [v for v in d[i].itervalues()])
        g.render_to_file('outp/bar_chart.svg')

    def __topic_chart(self):

        dt = self.__fetch_range()

        tl = []
        [[tl.append(j) for j in i['subjects'].split(', ')] for i in self.search('select_gtv', 'date', dt, 'subjects')]
        d = TF.get_freq(tl).most_common()

        g = pygal.StackedLine(logarithmic=True, x_label_rotation=30, fill=True, style=pygal.style.BlueStyle)
        g.title = 'Document frequency'
        g.x_labels = ['' for i in range(1, len(d))]
        g.add('topics', [v[1] for v in d])
        g.render_to_file('outp/topics.svg')

    def __topic_plot(self):

        matplotlib.rcParams['axes.unicode_minus'] = False
        #options.display.mpl_style = 'default'

        dt = self.__fetch_range()

        tl = []
        [[tl.append(j) for j in i['subjects'].split(', ')] for i in self.search('select_gtv', 'date', dt, 'subjects')]
        d = TF.get_freq(tl).most_common()

        df = DataFrame([v[1] for v in d], index=['' for i in range(0, len(d))], columns=list('t'))
        plt.figure(); df.plot(logy=True, logx=True); plt.show()

        print "Graph sucessfully created!"