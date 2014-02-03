__author__ = 'chris'

import json
import os
from logger import *


class Loader:

    def __init__(self, n):

        self.data = self.fetch_data(n)
        self.log = Logger()

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
        for art in self.data:
            print art

    def data_size(self):
        return len(self.data)

    def sample(self):
        return json.dumps(self.data[0], sort_keys=False, indent=4, separators=(',', ': '))

    def empty_docs(self, x):
        yield self.data[x]['comments']