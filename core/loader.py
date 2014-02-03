__author__ = 'chris'

import json
import os
from logger import *
from timer import *
from grapher import *


class Loader:

    def __init__(self, args):

        self.data = self.fetch_data(args['--test'])
        self.log = Logger()
        self.args = args
        self.time = Timer()
        self.graph = Grapher()

    def fetch_data(self, n):
        try:
            n = int(n)
        except TypeError:
            self.log.elog.error("Make sure the sample size is a number!")
            return

        data = []
        for file in os.listdir(os.getcwd()+"/res"):
            if n is not 0: n -= 1
            else: break
            if file.endswith(".txt"):
                with open(os.getcwd()+"/res/"+file, 'r') as f:
                    try:
                        jf = json.load(f)
                        data.append(jf)
                    except ValueError:
                        self.log.elog.error("JSON file " + str(f) + " was not recognized!")
        return data

    def data_wrapper(self, args):
        cmt_count, timeline = {'Populated Articles': None}, {'Article_dates': {}, 'Comment_dates': {}}
        sec_loop = False
        for x in range(0, len(self.data)):
            doc = self.data[x]
            cmt_list = doc.pop('comments')
            if args['-e']:
                cmt_count = self.count_docs(cmt_count, doc)
            if args['-t']:
                sec_loop = True
                timeline = self.time.time_docs(timeline, doc)
            if sec_loop:
                for i in range(0, len(cmt_list)):
                    cmt = cmt_list[i]
                    if args['-t']:
                        timeline = self.time.time_comms(timeline, cmt)
        self.graph.comm_chart(timeline)
        return self.snip(cmt_count.items() + timeline.items())

    def snip(self, dic):
        for k in dic:
            if not k[1]:
                del dic[dic.index(k)]
        return dic


    def data_size(self):
        return len(self.data)

    def sample(self):
        return json.dumps(self.data[0], sort_keys=False, indent=4, separators=(',', ': '))

    def count_docs(self, cmt_count, doc):
        cmt_count['Populated Articles'] += 1 if doc['comments'] else 0  # doc
        return cmt_count