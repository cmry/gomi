__author__ = 'chris'

import pygal
from core.mongo import Mongo
from heapq import merge
from collections import OrderedDict


class Grapher(Mongo):

    def route_args(self, args):
        if args['--dates']:
            self.date_chart()

    def date_chart(self):

        comment = [x['comment_date'].year for x in self.search('exists', 'comment_date').sort('comment_date')]
        article = [x['date'].year for x in self.search('exists', 'date').sort('date')]

        new_c, new_a, n_count = [0 for _ in range(0, len(comment)+len(article))], \
                                [0 for _ in range(0, len(comment)+len(article))], 0
        comb = list(merge(comment, article))
        scomb, dict1, dict2 = set(comb), {}, {}
        for x in scomb:
            dict1[x] = 0
            dict2[x] = 0
        for x in article:
            dict1[x] += 1
        for x in comment:
            dict2[x] += 1
        dict1, dict2 = OrderedDict(sorted(dict1.items(), key=lambda t: t[0])), \
                       OrderedDict(sorted(dict2.items(), key=lambda t: t[0]))


        line_chart = pygal.Bar()
        line_chart.title = 'Document frequency'
        line_chart.x_labels = [str(k) for k in sorted(scomb)]
        line_chart.add('Articles', [v for v in dict1.itervalues()])
        line_chart.add('Comments', [v for v in dict2.itervalues()])
        line_chart.render_to_file('outp/bar_chart.svg')