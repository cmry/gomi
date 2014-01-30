__author__ = 'chris'

import json
import os


class Loader:

    def __init__(self, n):

        self.data = self.fetch_data(n)

    def fetch_data(self, n):
        try:
            n = int(n)
        except TypeError:
            pass

        data = []
        for file in os.listdir(os.getcwd()+"/res"):
            if type(n) is int and n is not 0:
                n -= 1
            elif n is 0:
                break
            if file.endswith(".txt"):
                with open(os.getcwd()+"/res/"+file, 'r') as f:
                    try:
                        jf = json.load(f)
                        data.append(jf)
                    except ValueError:
                        pass
        return data

    def data_size(self):
        return len(self.data)

    def empty_docs(self):
        count = 0
        for x in range(0, len(self.data)):
            if self.data[x]['comments']:
                count += 1
        return len(self.data) - count