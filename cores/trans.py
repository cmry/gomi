__author__ = 'chris'
__file__ = 'trans.py'

import goslate
from central_core.query import *

class Translate:

    def __init__(self):
        """ Module relies on the Google Translate APi, very simple. """
        self.q = Query()

    def goslate(self, message, log):
        logt = log.push(-int(self.q.search(message).split(' ')[0]))
        gs = goslate.Goslate()
        for x in range(0, len(logt)):
            try:
                logt[x] = gs.translate(logt[x], 'en')
            except Exception as e:
                return "Corrupted cores! We're in luck."
        return '\n'.join(logt)
