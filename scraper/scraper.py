#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'chris'

import socket
from urllib2 import *
from random import shuffle
from TorCtl import TorCtl
from glob import glob
from os import path, chdir, listdir
from random import randint
from httplib import BadStatusLine

from bs4 import BeautifulSoup

from twkscraper import TwkScraper
from nuscraper import NuScraper

class Scraper:

    def __init__(self, minart, maxart, prod, interv, check, radar, log):
        """ Factory class to produce Articles according to different
        products. Tweakers.net and Nu.nl are implemented. """
        #call logger
        self.log = log
        self.interv = int(interv)
        self.check = check
        self.radar = radar

        #containers to store article objects from Beautifulsoup
        self.header = ''
        self.article = ''
        self.subject = ''
        self.comments = ''

        self.hashes = self.call_hash()
        self.arts = list(set(self.call_done(minart, maxart)).symmetric_difference(set(range(minart, maxart))))
        self.log.rlog.info("Roughly " + str(len(self.arts)) + " queries left for this scraper "+str(minart)+"-"+str(maxart))
        #used to randomize article visits while scraping
        shuffle(self.arts)

        #start scraping
        self.scrape_arts(self.arts, prod)

    def call_cats(self, site):
        """ Determines the categories that will be visited by the scraper. """
        if site is 't':
            cats = ['nieuws']
            return cats
        if site is 'n':
            cats = ['algemeen', 'nieuws', 'tech', 'wetenschap', 'data']
            shuffle(cats)
            return cats
        else:
            self.log.rlog.critical("Something went wrong with class cat, try again.")
            exit()

    def call_hash(self):
        try:
            chdir(os.getcwd()+"/res")
        except OSError:
            chdir(os.getcwd()+"/../res")
        hashes = glob('*.txt')
        chdir("../scraper/")
        return hashes

    def call_done(self, min, max):
        idlist = []
        try:
            chdir(os.getcwd()+"/log")
        except OSError:
            chdir(os.getcwd()+"/../log")
        for files in listdir("."):
            if files.endswith(".log"):
                with open(files, 'r') as fl:
                    fs = fl.read()
                    for x in set(re.findall('/[0-9]+/', fs)):
                        nx = int(x.strip('\/'))
                        if nx >= min and nx <= max:
                            idlist.append(nx)
        chdir("../scraper/")
        return idlist


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

    def scrape_cats(self, prod, entry, c=False, s=False, site=False):
        """ This method is an extention of scrape_arts. """

        cats = self.call_cats(prod)
        for cat in cats:
            site = self.call_site(prod, cat)
            site.art.id = hash(site.target+str(entry))

            if str(site.art.id)+".txt" in self.hashes:
                s = True
                break
            if not c:
                self.renew_connection()
                c = True
            if self.radar:
                self.stealth()
            if self.fetch_art(site, entry):
                #scrape operations
                self.fetch_target(site)
                self.fetch_nr(site, entry)
                self.fetch_art(site, entry)

                #site operations
                site.fetch_cont(self.article)
                site.fetch_head(self.header)
                site.fetch_subj(self.subject)
                site.fetch_comm(self.comments)

                #drop info in class and show
                site.art.struc_article()
                #print site.art.article
                del site
                return
        if site and not s:
            #if there's still a site, error
            self.log.rlog.info(str(site.target)+str(entry)+"/ "+"top level url error.")


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
            soup = BeautifulSoup(page)
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
        if self.interv != 0:
            time.sleep(randint(0, self.interv))
        dir = os.getcwd()+('/scraper/agents.txt' if 'scraper' not in os.getcwd() else '/agents.txt')
        with open(dir, 'r') as f:
            agents = f.readlines()
            return random.choice(agents).strip()

    def request(self, url):
        try:
            proxy_support = ProxyHandler({"http" : "127.0.0.1:8118"})
            opener = build_opener(proxy_support)
            opener.addheaders = [('User-agent', self.stealth())]
            return opener.open(url)
        except BadStatusLine:
            self.log.nlog.warning("Bad header, booting for new.")
            self.request(url)

    def renew_connection(self):
        saved_stdout, saved_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = open(os.devnull, "w")
        try:
            conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="ThisIsTor24")
            conn.send_signal("NEWNYM")
            conn.close()
        except AttributeError:
            self.log.nlog.warning("No onion for you.")
            time.sleep(60)
            self.renew_connection()
        sys.stdout, sys.stderr = saved_stdout, saved_stderr

    # TODO: critical permanently refused for ... problem
    def query(self, query):
        """ Queries a server and adds the provided user agent. """
        try:
            return self.request(query)
        except (HTTPError, socket.error, URLError) as e:
            if not e.reason:
                self.log.rlog.warning("Black magic shit, gtfo.")
                time.sleep(5)
                self.query(query)
            elif e.reason[0] is 104 or 'URLError' in e:
                self.log.rlog.warning("Connection reset by peer. Trying again.")
                time.sleep(5)
                self.query(query)
            elif 'Forbidden' in e.reason:
                self.log.rlog.warning("Access blocked")
                exit()
            elif 'Blocked' in e.reason:
                self.log.rlog.warning("Connection blocked! Waiting for new onion.")
                time.sleep(5)
                self.query(query)
            elif 'Too many open connections' in e.reason:
                self.log.rlog.warning("Too many connections, going to sleep.")
                time.sleep(randint(0, 600))
                self.query(query)
            elif 'Forwarding' in e.reason:
                self.log.rlog.warning("Tor isn't happy, let's take a nap.")
                time.sleep(randint(0, 600))
                self.query(query)
            elif 'Service Unavailable' in e.reason:
                self.log.rlog.warning("Service went bollocks, hybernation go.")
                time.sleep(randint(0, 600))
                self.query(query)
            elif 'Connection timeout' in e.reason:
                self.log.rlog.warning("Oops! Connection timed out.")
                time.sleep(randint(0, 600))
                self.query(query)
            elif 'No data received' in e.reason:
                self.log.rlog.warning("Tor took too long, resetting.")
                time.sleep(randint(0, 600))
                self.query(query)
            elif 'Found' in e.reason:
                return False
            else:
                #if url doesn't exist or is blocked
                self.log.nlog.critical("Shit went bad: "+str(e))


def main():
    if len(sys.argv) < 6:
        sys.stderr.write("Specify: (article range ##, ##, target, section, check, radar). \n")
        sys.exit(1)
    else:
        Scraper(int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]), int(sys.argv[4]), bool(sys.argv[5]), bool(sys.argv[6]))

if __name__ == '__main__':
    main()
