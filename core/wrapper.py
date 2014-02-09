#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 06.02'

import crunch
from copy import deepcopy


class Wrapper:

    def __init__(self, glob):


        self.glob = glob
        self.outp = {}


        # # this part wraps actions that are carried out directly on the
        # # sample set without extensive functions
        # if self.args['--loop']:
        #     dic = self.data_wrapper(mill)
        #     outp.update(dic)
        # else:
        #     if self.args['-l']:
        #         outp.update({'Data size:': mill.data_size()})
        #     if self.args['-s']:
        #         outp.update({'Data sample:': mill.sample()})
        #
        # # if there's any output to display, do so
        # if outp:
        #     for key, value in outp.iteritems():
        #         print key + " "*(20-len(key)) + str(value)

    # def data_wrapper(self, mill):
    #     """ This wrapper is used to place the different argument commands
    #     into different places of the function loop to handle everything in
    #     only one loop, saves computing time. Smart! """
    #
    #     # add dictionaries with output if more options are plugged
    #     output = {'cmt_count':    {'Populated Articles': 0, 'Empty Articles': 0},
    #               'timeline':     {'Article_dates': {}, 'Comment_dates': {}}
    #               }
    #     sec_loop = False  # required to omit the second loop by choice
    #
    #     for x in range(0, len(self.data)):
    #
    #         # per article, strip contents and split comments
    #         doc = deepcopy(mill.preprocess(self.data[x]))
    #         cmt_list = doc.pop('comments')
    #         # count erroneous docs
    #         if self.args['-e']:
    #             output['cmt_count'] = mill.count_docs(output['cmt_count'], self.data[x])  # avoid popped
    #         # generate timeline (1st loop)
    #         if self.args['-t']:
    #             sec_loop = True
    #             output['timeline'] = mill.time.time_docs(output['timeline'], doc)
    #         # comment loop actions
    #         if sec_loop:
    #             for i in range(0, len(cmt_list)):
    #                 cmt = mill.preprocess(cmt_list[i], 'comment_')
    #                 # generate timeline (2nd loop)
    #                 if self.args['-t']:
    #                     output['timeline'] = mill.time.time_comms(output['timeline'], cmt)
    #
    #     # final operations
    #     return mill.parse_output(output, self.args)