#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 05.02'

from aivb import AIVB
import json


class Mill(AIVB):

    def parse_output(self, output, args):
        """ Parse the obtained information in the right output and route
         it to the correct functions. """
        if args['-e']:
            output['cmt_count']['Empty Articles'] = self.data_size() - output['cmt_count']['Populated Articles']
        if args['-t']:
            pass  # self.graph.comm_chart(output['timeline'])
        return [self.snip(x) for x in output.itervalues()]

    def snip(self, dic):
        """ Remove dictionaries that yield an empty input. """
        dic = dic.items()
        for k in dic:
            print k
            if not k[1]:
                del dic[dic.index(k)]
        return dic

    def preprocess(self, jdoc, prep=str()):
        """ Preprocess pesty document errors. """
        date = [x.lower() for x in jdoc[prep+'date'].split()]
        try:
            int(date[0])
        except ValueError:
            date = [x for x in reversed(date)]
        jdoc[prep+'date'] = ' '.join(date)
        return jdoc

    def data_size(self):
        """ Return the size of the data for confirmation. """
        return len(self.data)

    def sample(self):
        """ Return a sample of the data. """
        return json.dumps(self.data[0], sort_keys=False, indent=4, separators=(',', ': '))

    def count_docs(self, cmt_count, doc):
        """ Count the amount of populated docs. """
        cmt_count['Populated Articles'] += 1 if doc['comments'] else 0  # doc
        return cmt_count