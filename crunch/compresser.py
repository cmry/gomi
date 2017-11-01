#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 03.07'

import os
from time import ctime
from glob import glob
from collections import OrderedDict


class Compresser:

    def __init__(self, source, tot=None):
        self.d = self.strip_file_info(source, tot)

    @staticmethod
    def get_files():
        os.chdir(os.getcwd()+"/../log")
        flist, fdict = glob('*.log'), {}
        for f in flist:
            (mode, ino, dev, nlink, uid, gid, size, atime, mtime, crtime) = os.stat(f)
            with open(f, 'r') as fr:
                fdict[f] = [ctime(int(crtime)), [x for x in fr.readlines()]]
        return fdict

    def strip_file_info(self, source, tot=None):
        cdict = {}
        for key, value in self.get_files().iteritems():
            stripl = []
            for line in value[1]:
                if (not tot and 'saved to' in line) or (tot and 'url error' in line) or (tot and 'saved to' in line) or (tot and 'already in' in line):
                    if (source == 't' and 'tweakers' in line) or (source == 'n' and 'nu.nl' in line):
                        stripl.append(line.split('scraper')[0][:-1])
                else:
                    continue
            if stripl:
                cdict[key] = [value[0], stripl]
        return cdict

    def hour_freq(self):
        d = self.d
        for k, v in d.iteritems():
            hfd = {}
            for x in range(0, 24):
                hfd[('0'+str(x) if x < 9 else str(x))+':00'] = 0
            for h in v[1]:
                for kh in hfd.iterkeys():
                    if kh[:-2] in h:
                        hfd[kh] += 1
            d[k].append(hfd)
        return d

    def hit_ph(self):
        d = self.hour_freq()
        for k, v in d.iteritems():
            totfr, toth = 0, 0
            for freq in v[2].itervalues():
                if freq != 0 and freq > 20:
                    totfr += freq
                    toth += 1
            d[k].append(float(totfr)/24)
        return d

    def bind_clusters(self, d, neg=None):
        bindd = {}
        for v in d.itervalues():
            bindd[v[0][:-10]+'00'] = []
        for v in d.itervalues():
            bindd[v[0][:-10]+'00'].append(v[3])
        for k, v in bindd.iteritems():
            bindd[k] = sum(v)/len(v) if neg else sum(v)
        return bindd

    def sort_date(self, d):
        d = OrderedDict(sorted(d.items(), key=lambda (k, v): v, reverse=True))
        return d