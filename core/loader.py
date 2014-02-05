#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.02'

import aivb  # main class
import json
import os


class Loader(aivb.AIVB):

    def fetch_data(self, n):
        """ This function opens all the files up to n given
         sample size, requires n to be an int, check was removed.
         default opens all the files. """

        data, n = [], int(n)

        while n is not 0:
            # as long as we're in the slice range, get files
            for fl in os.listdir(os.getcwd()+"/res"):
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