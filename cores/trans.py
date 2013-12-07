__author__ = 'chris'
__file__ = 'trans.py'

import goslate
from main.query import *

class Translate:

    def __init__(self):
        """ Module relies on the Google Translate APi, very simple. """
        self.q = Query()

    def goslate(self, message, log):
        lang = self.q.search(message).split(' ')[2]
        gs = goslate.Goslate()
        for x in range(0, len(log)):
            try:
                log[x] = gs.translate(log[x], lang)
            except Exception as e:
                print e
                return "Corrupted cores! We're in luck."
        return log