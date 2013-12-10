#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'chris'

from article import *
from re import compile

class TwkScraper:

    def __init__(self, cat, log):
        """ This class is used to scrape Tweakers.net. It will
        deliver site-specific patterns to the parent scraper. """

        #this class is tailored to tweakers.net
        self.target = 'http://www.tweakers.net/'+cat+'/'
        self.art = Article(log)
        self.charset = 'iso-8859-15'
        self.log = log

    def __del__(self):
        name = self.__class__.__name__

    def fetch_slices(self, soup):
        """ Returns categories into a dict to parent attributes for
            overall use, Tweakers specific """
        return {"header":   soup.find("h1", {"class": "ellipsis"}),
                "article":  soup.find("div", {"class": "articleColumn"}),
                "subject":  soup.find("div", {"class": "relevancyColumn"}),
                "comments": soup.find("div", {"id": "commentColumn"})}

    def fetch_cont(self, article):
        """ Grabs the date and text fields. """
        field = article.find("p", {"class": "author"})
        self.fetch_date(field)
        field = article.find("div", {"itemprop": "articleBody"})
        self.fetch_text(field)


    def fetch_date(self, date):
        """ Splits our date into seperate fields for storage (re-usable). """
        #this isn't re-usable
        date = self.fetch_tagcont(date.find('span'))
        datel = date.split(' ')

        self.art.date = str(datel[1]+' '+datel[2])
        self.art.year = str(datel[3])
        self.art.time = str(datel[4])

    def fetch_head(self, header):
        """ Prepares the title element (re-usable). """
        self.art.content['title'] = self.fetch_tagcont(header)

    def fetch_intro(self, intro):
        """ Prepares the intro element (re-usable). """
        self.art.content['intro'] = self.fetch_tagcont(intro)

    def fetch_text(self, text):
        """ Grabs text per p (re-usable?). """
        #this isn't re-usable
        field = text.find("p", {"class": "lead"})
        self.fetch_intro(field)

        text, textl = text.findAll('p'), []
        for p in text:
            if p is not field:
                textl.append(self.fetch_tagcont(p))

        self.art.content['text'] = '\n'.join(textl)

    def fetch_subj(self, subjfield):
        """ Grabs subjects from subject field. Sometimes
        not present, catch error. """
        subj = subjfield.find("div", {"class": "rbEntitylist"})

        subjl = []
        try:
            for a in subj.findAll('a'):
                subjl.append(self.fetch_tagcont(a))
        except AttributeError:
            subjl.append('')

        self.art.subj = ', '.join(subjl)

    def fetch_comm(self, comments):
        """ Grabs id, score, date and text from comments. """
        comments = comments.find("div", {"id": "reacties"})

        for comment in comments.findAll("div", {"class": "reactie"}):
            self.art.comment['comment_id'] = comment['id']

            header = comment.find("div", {"class": "reactieHeader"})
            self.fetch_commh(header)

            text = comment.find("div", {"class": "reactieContent"})
            self.fetch_commt(text)

            self.art.comments.append(self.art.comment)
            self.art.comment = {'comment_id': '',
                                'comment_user': '',
                                'comment_date': '',
                                'comment_year': '',
                                'comment_time': '',
                                'comment_text': '',
                                'comment_vote': ''}

    def fetch_commh(self, header):
        """ Picks required a's in the header object to parse date. """
        try:
            for a in header.findAll('a'):
                if str(a).startswith('<a class="score'):
                    self.art.comment['comment_vote'] = self.fetch_tagcont(a)
                elif str(a).startswith('<a href="http://tweakers.net/gallery'):
                    self.art.comment['comment_user'] = self.fetch_tagcont(a)
                elif str(a).startswith('<a class="date'):
                    datel = self.fetch_tagcont(a).split(' ')
                    self.art.comment['comment_date'] = str(datel[0]+' '+datel[1])
                    self.art.comment['comment_year'] = str(datel[2])
                    self.art.comment['comment_time'] = str(datel[3])
                    datel = []
        except (AttributeError, IndexError) as e:
            self.log.tlog.warning("Error "+str(e)+" occurred in current article.")
            pass

    def fetch_commt(self, text):
        """ Parses the comment text. """
        textl = []
        if text:
            for line in text:
                line = line.encode("utf-8")
                if str(line) == '<br/>':
                    textl.append('\n')
                elif str(line).startswith('<img alt'):
                    img = line.find('img')
                    if img and type(img) is not int:
                        textl.append(str(img['alt']))
                else:
                    line = str(line).replace('\n', '')
                    line = str(line).replace('\r', '')
                    line = str(line).replace('\t', '')
                    line = compile(r'<.*?>').sub('', line)
                    textl.append(line)

        self.art.comment['comment_text'] = ' '.join(textl)

    def fetch_tagcont(self, tagline):
        """ Overused tag content fetcher, clearer if in function. """
        try:
            return ''.join(tagline.findAll(text=True))
        except AttributeError:
            self.log.tlog.error("No introduction was found in current article.")
            return ""
