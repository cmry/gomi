#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 20.06'

from core.mongo import Mongo
from core.mapper import TF
from collections import OrderedDict
from pandas import *
from csv import reader, writer
from collections import Counter
import heapq
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
        l, scomb = self.get_freq(s, list(heapq.merge(s[0], s[1], s[2], s[3])))
        for x in l:
            d.append(OrderedDict(sorted(x.items(), key=lambda t: t[0])))
        return [d[0], d[2], d[1], d[3]], scomb

    def __fetchem(self, period, dt):
        l = [[], [], [], []]
        l[0] = self.__fetch_period('source', 'tweakers.net', 'date', period, dt)
        l[1] = self.__fetch_period('source', 'nu.nl', 'date', period, dt)
        if self.args['--comments']:
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
            if not self.args['--comments'] and 'Comments' in f[i]: pass
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
        plt.rc('font', **{'family': 'serif', 'serif': ['Palatino']})
        plt.rc('text', usetex=True)

        tl = []
        [[tl.append(j) for j in i['subjects'].split(', ')] for i in self.search('select_gtv', 'date', dt, 'subjects')]
        d = TF.get_freq(tl).most_common()

        df = DataFrame([v[1] for v in d], index=['' for i in range(0, len(d))], columns=list('t'))
        plt.figure(); df.plot(logy=True, logx=True)
        plt.xlabel(r'\textbf{time} (s)')  # edit
        plt.ylabel(r'\textit{voltage} (mV)', fontsize=16)
        plt.savefig('tex_demo')

        print "Graph sucessfully created!"

    @staticmethod
    def convergence_plot(out_name, line_name, x, y):

        plt.rc('font', **{'family': 'serif', 'serif': ['Palatino']})
        plt.rc('text', usetex=True)
        line_name = line_name+'s' if 't' in line_name else line_name

        matplotlib.rcParams['axes.unicode_minus'] = False
        df = DataFrame([[li] for li in x], index=[i for i in y], columns=[line_name])

        plt.figure(); df.plot(color='black', linewidth=2, fontsize=40)
        plt.xlabel(r'epochs', fontsize=40)  # edit
        plt.ylabel(r'mean weight', fontsize=40)

        print 'outp/'+out_name+'_plot.pdf'
        plt.savefig('outp/'+out_name+'_plot.pdf')

        print "Graph sucessfully created!"

    def dateplot(self):
        reltop = ['Privacy', 'NSA', 'PRISM', 'Edward_Snowden', 'Prism', 'prism', 'privacy']

        with open('/home/chris/mcode/outp/comment_all_ti.csv', 'r') as f:
            with open('/home/chris/mcode/outp/article_all_ti.csv', 'r') as f2:
                r, r2 = reader(f), reader(f2)
                c, c2 = self.__csvcounter(r, reltop, 'c'), self.__csvcounter(r2, reltop, 'a')

        src = ['N', 'T']
        prd = ['ESP', 'OSP', 'ISP']
        wek = [str(x) for x in range(1, 27)]
        for s in src:
            for p in prd:
                for w in wek:
                    if p == 'OSP' and int(w) > 20:
                        pass
                    else:
                        if not c['c_'+s+'_'+p+'_'+w]:
                            c['c_'+s+'_'+p+'_'+w] = 0

        with open('/home/chris/mcode/outp/check.csv', 'w') as f:
            w = writer(f)
            i = 0
            for k, v in c.iteritems():
                i += 1
                w.writerow([str(i)+'D']+k[2:].split('_')+[v]+[c2['a_'+k[2:]]])

    @staticmethod
    def __csvcounter(f, rel, app):
        c = Counter()
        for a in f:
            if any(i in rel for i in a[5].split()):
                source, date, period, topic = a[2], a[3], a[4], a[5]
                if '2013-06' in date:
                    period = 'SP'  # error fix in labels
                if '2013-11' in date or '2013-12' in date: # <------------ DIT IS HET PROBLEEM
                    period = 'OSP' # error fix in labels
                if period != 'NaP' and '2014-04' not in date and '2014-05' not in date and '2014-06' not in date:
                    xd = a[3].split(' ')[0].split('-')
                    dl = datetime.date(int(xd[0]), int(xd[1]), int(xd[2])).isocalendar()[1]
                    if dl > 26:
                        dl -= 26
                    ll = ['T' if source == 'tweakers.net' else 'N',     # source label
                              period if period != 'SP' else 'ISP',      # period label
                              str(dl)]                                  # week label
                    c[app+'_'+'_'.join(ll)] += 1
        return c

    @staticmethod
    def general_plot():

        nunltcmt = [33, 37, 3, 14, 138, 3070, 2431, 1058, 758, 1008, 1013, 582, 343, 186, 270]
        tnettcmt = [222, 288, 49, 112, 289, 1211, 473, 640, 722, 1370, 1115, 1404, 995, 956, 556]
        nunltart = [8, 11, 9, 11, 18, 108, 75, 20, 44, 61, 78, 31, 29, 26, 23]
        tnettart = [19, 28, 9, 29, 24, 68, 40, 42, 42, 88, 98, 73, 66, 53, 53]

        out_name = 'cmtart_ontopic'
        line_name = ['nu.nl cmt', 't.net cmt', 'nu.nl art', 't.net art']

        plt.rc('font', **{'family': 'serif', 'serif': ['Palatino']})
        plt.rc('text', usetex=True)

        matplotlib.rcParams['axes.unicode_minus'] = False
        df = DataFrame([[n, t, n2, t2] for n, t, n2, t2 in zip(nunltcmt, tnettcmt, nunltart, tnettart)], index=date_range('1/1/2013', periods=15, freq='M'), columns=line_name)

        plt.figure(); df.plot(linewidth=2, colormap='summer', logy=True)
        plt.xlabel(r'time', fontsize=12)  # edit
        plt.ylabel(r'frequency', fontsize=12)

        plt.subplots_adjust(bottom=0.2)
        plt.savefig('outp/'+out_name+'_plot.pdf')

        print "Graph sucessfully created!"

        wnunl = [float(a)/float(b) for a, b in zip(nunltcmt, nunltart)]
        wtnet = [float(a)/float(b) for a, b in zip(tnettcmt, tnettart)]

        out_name = 'wgh_ontopic'
        line_name = ['nu.nl wgh', 't.net wgh']

        matplotlib.rcParams['axes.unicode_minus'] = False
        df = DataFrame([[n, t] for n, t, in zip(wnunl, wtnet)], index=date_range('1/1/2013', periods=15, freq='M'), columns=line_name)

        plt.figure(); df.plot(linewidth=2, colormap='summer', logy=False)
        plt.xlabel(r'time', fontsize=12)  # edit
        plt.ylabel(r'frequency', fontsize=12)

        plt.subplots_adjust(bottom=0.2)
        plt.savefig('outp/'+out_name+'_plot.pdf')

        print "Graph sucessfully created!"

        nunlocmt = [313, 397, 394, 574, 520, 475, 357, 513, 627, 480, 575, 316, 479, 333, 783]
        tnetocmt = [510, 650, 685, 911, 720, 942, 857, 803, 1012, 935, 1227, 894, 1124, 1013, 939]
        nunloart = [89, 98, 121, 142, 136, 124, 95, 86, 100, 92, 100, 71, 110, 77, 122]
        tnetoart = [158, 194, 215, 240, 195, 181, 180, 190, 188, 217, 232, 181, 214, 187, 185]

        out_name = 'cmtart_offtopic'
        line_name = ['nu.nl cmt', 't.net cmt', 'nu.nl art', 't.net art']

        plt.rc('font', **{'family': 'serif', 'serif': ['Palatino']})
        plt.rc('text', usetex=True)

        matplotlib.rcParams['axes.unicode_minus'] = False
        df = DataFrame([[n, t, n2, t2] for n, t, n2, t2 in zip(nunlocmt, tnetocmt, nunloart, tnetoart)], index=date_range('1/1/2013', periods=15, freq='M'), columns=line_name)

        plt.figure(); df.plot(linewidth=2, colormap='summer', logy=True)
        plt.xlabel(r'time', fontsize=12)  # edit
        plt.ylabel(r'frequency', fontsize=12)

        plt.subplots_adjust(bottom=0.2)
        plt.savefig('outp/'+out_name+'_plot.pdf')

        print "Graph sucessfully created!"

        wnunl = [float(a)/float(b) for a, b in zip(nunlocmt, nunloart)]
        wtnet = [float(a)/float(b) for a, b in zip(tnetocmt, tnetoart)]

        out_name = 'wgh_offtopic'
        line_name = ['nu.nl wgh', 't.net wgh']

        matplotlib.rcParams['axes.unicode_minus'] = False
        df = DataFrame([[n, t] for n, t, in zip(wnunl, wtnet)], index=date_range('1/1/2013', periods=15, freq='M'), columns=line_name)

        plt.figure(); df.plot(linewidth=2, colormap='summer', logy=False)
        plt.xlabel(r'time', fontsize=12)  # edit
        plt.ylabel(r'frequency', fontsize=12)

        plt.subplots_adjust(bottom=0.2)
        plt.savefig('outp/'+out_name+'_plot.pdf')


if __name__ == '__main__':
    g = Grapher('')
    g.dateplot()