__author__ = 'chris'

import socket
from urllib2 import *
from bs4 import BeautifulSoup
from random import shuffle
from time import sleep
from random import randint
from os import path, chdir, listdir
from twkscraper import TwkScraper
from nuscraper import NuScraper
from logger import Logger


class Scraper:

    def __init__(self, minart, maxart, prod, interv, check, radar):
        """ Factory class to produce Articles according to different
        products. Tweakers.net and Nu.nl are implemented. """
        #call logger
        self.log = Logger()
        self.interv = interv
        self.check = check
        self.radar = radar

        #containers to store article objects from Beautifulsoup
        self.header = ''
        self.article = ''
        self.subject = ''
        self.comments = ''

        #used to randomize article visits while scraping
        self.arts = list(range(minart, maxart))
        shuffle(self.arts)

        #start scraping
        self.scrape_arts(self.arts, prod)

    def call_cats(self, site):
        """ Determines the categories that will be visited by the
            scraper. """
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


    def call_site(self, site, cat):
        if site is 't':
            return TwkScraper(cat, self.log)
        elif site is 'n':
            return NuScraper(cat, self.log)
        else:
            self.log.rlog.critical("Something went wrong with class init, try again.")
            exit()

    def scrape_arts(self, arts, prod):
        """ This method visits each entry in self.arts and extracts information.
            It uses the seperate method scrape_cats to break."""

        for entry in arts:
            self.scrape_cats(prod, entry)

    def scrape_cats(self, prod, entry):
        """ This method is an extention of scrape_arts. """

        for cat in self.call_cats(prod):
            self.log.halt = False
            site = self.call_site(prod, cat)

            #check if file exists, else prepare hash
            if self.gen_id(site, entry):
                return

            while not self.log.halt:
                if self.radar:
                    self.stealth()
                if self.fetch_art(site, entry):

                        #scrape operations
                        self.fetch_target(site)
                        self.fetch_nr(site, entry)
                        self.fetch_art(site, entry)

                        #site operations
                        site.fetch_err(self.article)
                        site.fetch_cont(self.article)
                        site.fetch_head(self.header)
                        site.fetch_subj(self.subject)
                        site.fetch_comm(self.comments)

                        #drop info in class and show
                        site.art.struc_article()
                        #print site.art.article
                        del site
                        return
                else:
                    #abort on non-existent articles
                    self.log.halt = True
        if site:
            #if there's still a site, error
            self.log.rlog.critical(str(site.target)+str(entry)+"/ "+"top level url error.")

    def gen_id(self, site, nr):
        """ Generates a hash based on url + article number (re-usable). """
        site.art.id = hash(site.target+str(nr))
        if path.isfile("res/"+str(site.art.id)+".txt"):
            self.log.rlog.info(str(site.art.id)+" already in log.")
            return True

        if 'nu.nl' in site.target:
            chdir(os.getcwd()+"/log")
            for files in listdir("."):
                if files.endswith(".log"):
                    with open(files, 'r') as fl:
                        if str(nr) in fl.read():
                            chdir("..")
                            self.log.rlog.info(str(site.art.id)+" already in log.")
                            return True
            chdir("..")

    def fetch_target(self, site):
        """ Used to abbreviate our target (re-usable). """
        target = site.target.split('http://www.')[1]
        target = target.split('/')[0]
        site.art.source = target

    def fetch_nr(self, site, entry):
        """ Store the article number we're at (re-usable). """
        site.art.nr = entry

    def fetch_art(self, site, nr):
        """ Used to grab the article defined by artnr and set the attributes
        to store the article information in (re-usable). """

        page = self.query(site.target+str(nr)+'/')

        if page:
            #added encoding, hopefully solves encoding problems throughout
            charset = page.headers['content-type'].split('charset=')[-1]
            soup = BeautifulSoup(page.read().decode(charset))
            slices = site.fetch_slices(soup)
            self.header = slices['header']
            self.article = slices['article']
            self.subject = slices['subject']
            self.comments = slices['comments']
            return True
        else:
            #yield error if we don't have a page for some reason
            return False

    def stealth(self):
        """ If we want to work with some diligence (especially in the case of
            sites with anti-scrape methods), change headers and time-out. """
        sleep(randint(0, self.interv))
        with open('agents.txt', 'r') as f:
            agents = f.readlines()
            return random.choice(agents).strip()

    def query(self, query):
        """ Queries a server and adds the provided user agent. """
        try:
            opener = build_opener()
            opener.addheaders = [('User-agent', self.stealth())]
            page = opener.open(query)
            return page
        except (HTTPError, socket.error) as e:
            if e.reason[0] == 104:
                self.log.nlog.warning("Connection reset by peer. Trying again.")
                time.sleep(5)
                self.query(query)
            else:
                #if url doesn't exist or is blocked
                return False


def main():
    if len(sys.argv) < 6:
        sys.stderr.write("Specify: (article range ##, ##, target, section, check, radar). \n")
        sys.exit(1)
    else:
        Scraper(int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]), int(sys.argv[4]), bool(sys.argv[5]), bool(sys.argv[6]))

if __name__ == '__main__':
    main()