__author__ = 'chris'

import socket
from urllib2 import *
from random import shuffle
from core.logger import Logger


class Spider:

    def __init__(self, minart, maxart, prod):
        """ Factory class to produce Articles according to different
        products. Tweakers.net and Nu.nl are implemented. """
        #call logger
        self.log = Logger()
        self.target = ''

        #used to randomize article visits while scraping
        self.arts = list(range(minart, maxart))
        shuffle(self.arts)

        #start scraping
        self.spider_arts(self.arts, prod)

    def call_cats(self, site):
        """ Determines the categories that will be visited by the scraper. """
        if site is 't':
            cats = ['nieuws']
            return cats
        if site is 'n':
            cats = ['algemeen', 'nieuws', 'tech', 'wetenschap',
                    'geldzaken', 'ondernemen', 'schuldencrisis',
                    'sport', 'achterklap', 'opmerkelijk', 'film',
                    'muziek', 'boek', 'media', 'cultuur', 'data']
            shuffle(cats)
            return cats
        else:
            self.log.rlog.critical("Something went wrong with class cat, try again.")
            exit()

    def spider_arts(self, arts, prod):
        """ This method visits each entry in self.arts and extracts information.
            It uses the seperate method scrape_cats to break."""

        for entry in arts:
            self.spider_cats(prod, entry)

    def spider_cats(self, site, entry):
        """ This method is an extention of scrape_arts. """

        for cat in self.call_cats(site):
            self.site = 'http://www.nu.nl/'+cat+'/'
            if self.query(self.site+str(entry)+'/'):
                with open('stack.txt', 'ab+') as f:
                    f.write(str(self.site + ", " + cat + ", " + entry + "\n"))
                self.log.nlog.info("Stacked " + self.site + ", " + cat + ", " + entry)
                del self.site
                return
            else:
                #abort on non-existent articles
                self.log.halt = True
        if self.site:
            #if there's still a site, error
            self.log.rlog.critical(str(self.site)+str(entry)+"/ "+"top level url error.")

    def stealth(self):
        """ If we want to work with some diligence (especially in the case of
            sites with anti-scrape methods), change headers and time-out. """
        with open('agents.txt', 'r') as f:
            agents = f.readlines()
            return random.choice(agents).strip()

    def query(self, query):
        """ Queries a server and adds the provided user agent. """
        try:
            try:
                opener = build_opener()
                opener.addheaders = [('User-agent', self.stealth())]
                page = opener.open(query)
                return page
            except HTTPError:
                return
        except (socket.error, URLError) as e:
            self.log.nlog.warning("Connection reset by peer. Trying again.")
            time.sleep(5)
            self.query(query)

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Specify: (article range ##, ##, target). \n")
        sys.exit(1)
    else:
        Spider(int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]))

if __name__ == '__main__':
    main()