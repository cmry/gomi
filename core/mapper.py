#!/usr/bin/env python

__author__ = 'chris'

from collections import Counter
from collections import OrderedDict
from pandas import DataFrame
from copy import deepcopy


class TF:

    def __init__(self, docl, freqd=dict()):
        for i in range(0, len(docl)):
            cur_d = self.get_freq(docl[i].split())
            freqd['doc'+str(i+1)] = cur_d
        print self.struc_M(freqd)

    @staticmethod
    def get_freq(doc):
        freqd = Counter()
        for word in doc:
            freqd[word] += 1
        return freqd

    def od(self, d):
        return OrderedDict(sorted(d.items(), key=lambda (k, v): k))

    def fill(self, d, v):
        x = deepcopy(d)
        for tkey, value in x.iteritems():
            for key in v.iterkeys():
                if key not in value:
                    d[tkey].update({key: 0})
        return d

    def struc_M(self, freqd):
        vocab = Counter()
        for value in freqd.itervalues():
            vocab += value
        M = DataFrame.from_dict(self.od(self.fill(freqd, vocab)), orient='index')
        return M

if __name__ == '__main__':
    # teststuff
    docl = ['derp derp \n herp derp', 'derp herp \n lerp derp', 'verp merp']
    tf = TF(docl)