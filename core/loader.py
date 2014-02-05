#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.02'

import json
import os
import sys


class Loader:

    def __init__(self, log):
        """ This class is used to load an n amount of data and
        pass it back to the main function, nothing more. """

        self.data = []
        self.log = log
        # TODO: build dump fuction
        # TODO: continue working on wrapper

    def fetch_data(self, n):
        """ This function opens all the files up to n given
         sample size, requires n to be an int, check was removed.
         default opens all the files. """

        data, n, t = [], int(n), int(n)

        # as long as we're in the slice range, get files
        for fl in os.listdir(os.getcwd()+"/res"):
            self.perc(n, t)
            if n < 1: print "\n"; break
            if fl.endswith(".txt"):  # avoid litter
                with open(os.getcwd()+"/res/"+fl, 'r') as f:
                    try:
                        jf = json.load(f)
                        data.append(jf)
                    except ValueError:  # this might be unnecessary
                        self.log.llog.warning("JSON file " + str(f) + " was not recognized!")
                n -= 1
            else:
                self.log.llog.warning("A non .txt was detected!")
        self.log.llog.info("Database was loaded!")
        return data

    def perc(self, curr, tot):
        """ Small function to display percentage of total for
        decreasing range. """
        print >> sys.stdout, "\r%d%%" % (int(float(100)-(float(curr)/float(tot)*100))),
        sys.stdout.flush()