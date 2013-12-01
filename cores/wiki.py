__author__ = 'chris'

from wiki2plain import Wiki2Plain
from wikipedia import Wikipedia
from main.query import *

class Wiki:

    def __init__(self):
        """ Implementation of modules from https://github.com/jinghe """
        self.q = Query()

    def wiki(self, message):
        query, wiki = self.q.search(message), Wikipedia('en')
        try:
            return self.q.cut(Wiki2Plain(wiki.article(query), query).text)
        except:
            return "The Enrichment Center regrets to inform you that this next test is impossible."