__author__ = 'chris'

import pygal
from core.mongo import Mongo
from collections import OrderedDict


class Grapher(Mongo):

    def route_args(self, args):
        if args['--dates']:
            self.date_chart()

    def date_chart(self):

        comment = [x for x in self.articles.search('exists', 'comment_date')]

        #comment = dict['Comment_dates']
        #article = dict['Article_dates']
        #comment = OrderedDict(sorted(comment.items(), key=lambda (k, v): v, reverse=True))
        #article = OrderedDict(sorted(article.items(), key=lambda (k, v): v, reverse=True))
        #
        #dates = []
        #arts = []
        #cmts = []
        #
        #for k, v in comment:
        #    if k not in dates:
        #        dates.append(k)
        #    if k not in article.keys():
        #        arts.append(None)
        #
        #
        #line_chart = pygal.Line()
        #line_chart.title = 'Document frequency'
        #line_chart.x_labels = map(str, [x for x in dict])
        #line_chart.add('Articles', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
        #line_chart.add('Comments',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
        #line_chart.render()