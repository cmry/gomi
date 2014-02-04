__author__ = 'chris'

import json
import os
from logger import *
from copy import deepcopy
from timer import *
from grapher import *


class Loader:

    def __init__(self, args, log):

        self.data = self.fetch_data(args['--slice'])
        self.log = log
        self.args = args
        self.time = Timer()
        self.graph = Grapher()

    def fetch_data(self, n):
        """ This function opens all the files up to n given
         sample size, requires n to be an int, check was removed.
         default opens all the files. """

        data, n = [], int(n)
        for file in os.listdir(os.getcwd()+"/res"):
            if n is not 0: n -= 1
            else: break  # break if limit is reached
            if file.endswith(".txt"):
                with open(os.getcwd()+"/res/"+file, 'r') as f:
                    try:
                        jf = json.load(f)
                        data.append(jf)
                    except ValueError:  # this might be unnecessary
                        self.log.elog.error("JSON file " + str(f) + " was not recognized!")
        return data

    def data_wrapper(self, args):
        """ This wrapper is used to place the different argument commands
        into different places of the function loop to handle everything in
        only one loop, saves computing time. Smart! """

        # add dictionaries with output if more options are plugged
        output = {'cmt_count':    {'Populated Articles': 0, 'Empty Articles': 0},
                'timeline':     {'Article_dates': {}, 'Comment_dates': {}}
                }
        sec_loop = False  # required to omit the second loop by choice

        for x in range(0, len(self.data)):

            # per article, strip contents and split comments
            doc = deepcopy(self.preprocess(self.data[x]))
            cmt_list = doc.pop('comments')
            # count erroneous docs
            if args['-e']:
                output['cmt_count'] = self.count_docs(output['cmt_count'], self.data[x])  # avoid popped
            # generate timeline (1st loop)
            if args['-t']:
                sec_loop = True
                output['timeline'] = self.time.time_docs(output['timeline'], doc)
            # comment loop actions
            if sec_loop:
                for i in range(0, len(cmt_list)):
                    cmt = self.preprocess(cmt_list[i], 'comment_')
                    # generate timeline (2nd loop)
                    if args['-t']:
                        output['timeline'] = self.time.time_comms(output['timeline'], cmt)

        # final operations
        return self.parse_output(output, args)

    def parse_output(self, output, args):
        """ Parse the obtained information in the right output and route
         it to the correct functions. """
        if args['-e']:
            output['cmt_count']['Empty Articles'] = self.data_size() - output['cmt_count']['Populated Articles']
        if args['-t']:
            self.graph.comm_chart(output['timeline'])
        return [self.snip(x) for x in output.itervalues()]

    def snip(self, dic):
        """ Remove dictionaries that yield an empty input. """
        dic = dic.items()
        for k in dic:
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