__author__ = 'chris'

from wiki2plain import Wiki2Plain
from wikipedia import Wikipedia
from query import *

class Wiki:

    def __init__(self):
        self.q = Query()

    def wiki(self, message):
        query = self.q.search(message)

        lang = 'en'
        wiki = Wikipedia(lang)

        try:
            raw = wiki.article(query)
        except:
            raw = None

        if raw:
            wiki2plain = Wiki2Plain(raw,query)
            return self.q.cut(wiki2plain.text)
        else:
            return "The Enrichment Center regrets to inform you that this next test is impossible."