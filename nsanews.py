__author__ = 'chris'
__file__ = 'nsanews.py'

from urllib2 import urlopen
from bs4 import BeautifulSoup


class NSA:

    def __init__(self):

        self.keys = ['NSA', 'Snowden', 'FBI', 'privacy']

    def grab_daily(self):
        soup, res = BeautifulSoup(urlopen('http://www.tweakers.net/')), []

        for hl in soup.findAll(attrs={'class': compile(r".*\bhighlights\b.*")}):
            for a in hl.findAll('a'):
                if '#reacties' not in a['href'] and 'nieuws' in a['href']:
                    res.append(a['href'])
        if res:
            return self.search_daily(res)
        else:
            return "Corrupted cores! We're in luck."

    def search_daily(self, res):

        newres = []
        for art in res:
            soup = BeautifulSoup(urlopen(art))
            for p in soup.findAll('p'):
                for key in self.keys:
                    if key in str(p):
                        head = str(str(soup.find("p", {"class": "lead"})).replace('<p class="lead">', '')).replace('</p>', '')
                        if head not in newres:
                            newres.append(head)
                            newres.append(str(art))
                        break
        if not newres:
            yield "The good news is... well, none so far, to be honest. I'll get back to you on that."
        else:
            yield '\n'.join(str(line) for line in newres)