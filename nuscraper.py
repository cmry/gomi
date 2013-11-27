__author__ = 'chris'

import socket
from article import *
from mlstrip import *
from urllib2 import *
from bs4 import BeautifulSoup
from re import compile
from time import sleep, strptime


class NuScraper:

    def __init__(self, cat, log):
        """ This class is used to scrape nu.nl. It will
         create an Article class for each entry received from our tweakers
         list and store these in a database (re-usable). """

        #this class is tailored to nu.nl
        self.target = 'http://www.nu.nl/'+cat+'/'
        self.art = Article(log)
        self.log = log

    def __del__(self):
        name = self.__class__.__name__

    def fetch_slices(self, soup):
        """ Returns categories into a dict to parent attributes for
            overall use, Tweakers specific """
        res = {"header":   soup.find("div", {"class": "header"}),
               "article":  soup.find("div", {"id": "leadarticle"}),
               "subject":  soup.find("div", {"class": "widgetsection vspacious tags"}),
               "comments": self.fetch_nujij(soup)}
        return res

    def fetch_err(self, error_focus):
        """ Checks if the website yeilds 404 or comments are empty. """
        if error_focus.find(text="De pagina die u op onze site zocht kan helaas niet gevonden worden."):
            self.log.nlog.critical("404")
            self.log.halt = True
        if error_focus.find(text="Reactie plaatsen > Stap 1"):
            self.log.nlog.critical("NoComments")
            self.log.halt = True

    def fetch_cont(self, article):
        """ Grabs the date and text fields. """
        field = article.find("div", {"class": "dateplace-data"})
        self.fetch_date(self.fetch_tagcont(field))
        field = article.find("div", {"class": "content"})
        self.fetch_text(field)

    def fetch_date(self, date):
        """ Splits our date into seperate fields for storage (re-usable). """
        datel = date.split(' ')
        date_stack = []
        for entry in datel:
            entry = entry.replace('\n', '').replace('\t', '').replace(' ', '')
            if self.check_day(entry):
                date_stack.append(entry)
            if self.check_month(entry):
                date_stack.append(entry)
            if len(date_stack) is 2:
                self.art.date = ' '.join(date_stack)
            if self.check_year(entry):
                self.art.year = entry
            if self.check_time(entry):
                self.art.time = str(entry)
                break

    def check_time(self, field):
        """ Check if field is a time. """
        try:
            strptime(field, '%H:%M')
            return True
        except ValueError:
            return False

    def check_day(self, field):
        """ Check if field is a day. """
        try:
            day = [int(x) for x in str(field)]
            if len(day) is 1 or len(day) is 2:
                return True
            else:
                return False
        except ValueError:
            return False

    def check_month(self, field):
        """ Check if field is a Dutch month. """
        monthl = ['januari', 'februari', 'maart',
                  'april', 'mei', 'juni',
                  'juli', 'augstus', 'september',
                  'oktober', 'november', 'december']

        if field in monthl:
            return True
        else:
            return False

    def check_year(self, field):
        """ Check if field is a year. """
        try:
            strptime(field[:-2], '%y')
            return True
        except ValueError:
            return False

    def fetch_head(self, header):
        """ Prepares the title element (re-usable). """
        header = header.find('h1')
        self.art.content['title'] = self.fetch_tagcont(header)

    def fetch_intro(self, intro):
        """ Prepares the intro element (re-usable). """
        self.art.content['intro'] = self.fetch_tagcont(intro)

    def fetch_text(self, text):
        """ Grabs text per p (re-usable?). """
        #this isn't re-usable
        field = text.find("h2")
        self.fetch_intro(field)

        text, textl = text.findAll('p'), []
        for p in text:
            if p is not field:
                textl.append(self.fetch_tagcont(p))

        self.art.content['text'] = '\n'.join(textl)

    def fetch_subj(self, subjfield):
        """ Grabs subjects from subject field. """
        if subjfield:
            subjl = []
            for li in subjfield.findAll("li"):
                subjl.append(self.fetch_tagcont(li))

            self.art.subj = ', '.join(subjl)
        else:
            self.art.subj = 'None'

    def fetch_comm(self, comments):
        """ Grabs id, score, date and text from comments. """

        try:
            pages = comments.find("div", {"class": "pages"})

            link_list, comment_list = [], []
            comment_list.append(comments)

            for link in set(pages.findAll('a')):
                link_list.append(link['href'])

            if link_list:
                for href in set(link_list):
                    try:
                        page = urlopen('http://www.nujij.nl'+href)
                        nu_soup = BeautifulSoup(page)
                        comment_list.append(nu_soup.find("div", {"class": "bericht-subsectie"}))
                    except (HTTPError, socket.error) as e:
                        #if url doesn't exist or is blocked
                        if e.reason[0] == 104:
                            self.log.nlog.warning("Connection reset by peer. Trying again.")
                            time.sleep(5)
                            self.fetch_comm(comments)
                        else:
                            #if url doesn't exist or is blocked
                            self.log.nlog.error(str(e)+': NuJij not found for: '+href)

            for comment_section in comment_list:
                for comment in comment_section.find("ol", {"class": "reacties"}).findAll("li"):
                    try:
                        self.art.comment['comment_id'] = comment['id']
                        self.fetch_commh(comment)

                        text = self.fetch_tagcont(comment.find("div", {"class": "reactie-body"}))
                        self.fetch_commt(text)

                        self.art.comments.append(self.art.comment)
                        self.art.comment = {'comment_id': '',
                                            'comment_user': '',
                                            'comment_date': '',
                                            'comment_year': '',
                                            'comment_time': '',
                                            'comment_text': '',
                                            'comment_vote': ''}
                    except KeyError:
                        pass

        except (AttributeError, TypeError) as e:
            self.log.nlog.error(str(e)+': something fucked up.')
            pass

    def fetch_commh(self, header):
        """ Picks required a's in the header object to parse date. """
        try:
            self.art.comment['comment_vote'] = " ".join(self.fetch_tagcont(x)
                                                        for x in header.findAll("div", {"class": "reactie-saldo"}))
            self.art.comment['comment_user'] = self.fetch_tagcont(header.find("strong"))
            datel = header.find("span", {"class": "tijdsverschil"})['publicationdate'].split(' ')
            self.art.comment['comment_date'] = str(datel[0]+' '+datel[1][:-1])
            self.art.comment['comment_year'] = str(datel[2])
            self.art.comment['comment_time'] = str(datel[3][:-3])
        except (TypeError, AttributeError) as e:
            self.log.nlog.error(str(e)+': error while processing comments.')

    def fetch_commt(self, text):
        """ Parses the comment text. """
        textl = []
        if text:
            #try:
            #    text = text.encode("utf-8")
            #except UnicodeDecodeError:
            #    self.log.nlog.error("Unicode error!")
            if str(text) == '<br/>':
                textl.append('\n')
            elif str(text).startswith('<img alt'):
                img = text.find('img')
                if img and type(img) is not int:
                    textl.append(str(img['alt']))
            else:
                text = str(text).replace('\n', '')
                text = str(text).replace('\r', '')
                text = str(text).replace('\t', '')
                text = compile(r'<.*?>').sub('', text)
                textl.append(text)

        self.art.comment['comment_text'] = ' '.join(textl)
#----------------------------------------------------------------------

    def fetch_nujij(self, soup, tries=None):
        """ Recursive website visitation of nu and nujij,
            ugliest fucking function ever. """

        try:
            backlink = str(soup.find("link", {"rel": "canonical"})['href']).replace('http://www.nu.nl/', '')
        except TypeError:
            try:
                backlink = str(soup.find("meta", {"property": "og:url"})['content']).replace('http://www.nu.nl/', '')
            except TypeError:
                backlink = "wtfnu"

        try:
            page = urlopen('http://m.nu.nl/'+backlink)
        except (HTTPError, socket.error) as e:
            #if url doesn't exist or is blocked
            if e.reason[0] == 104:
                self.log.nlog.warning("Connection reset by peer. Trying again.")
                time.sleep(5)
                self.fetch_nujij(soup, tries)
            else:
                self.log.nlog.warning(str(e)+' mobile site refused, trying again.')
                if tries is None:
                    tries = 1
                else:
                    tries += 1
                sleep(1)
                if tries < 30:
                    self.fetch_nujij(soup, tries)
                else:
                    self.log.nlog.critical(str(e)+' mobile site permanently refused.')
                    self.log.halt = True
                page = None

        if page:
            secsoup = BeautifulSoup(page)
            target = secsoup.find("li", {"class": "nujij last"})
            lynx = target.find("a")['href']

            try:
                nujij = urlopen(lynx)
            except (HTTPError, socket.error) as e:
            #if url doesn't exist or is blocked
                if e.reason[0] == 104:
                    self.log.nlog.warning("Connection reset by peer. Trying again.")
                    time.sleep(5)
                    self.fetch_nujij(soup, tries)
                else:
                    #if url doesn't exist or is blocked
                    self.log.nlog.critical(str(e)+' mobile site refused during other page visit.')
                    self.log.halt = True
                    return None

            if nujij:
                nu_soup = BeautifulSoup(nujij)
                return nu_soup.find("div", {"class": "bericht-subsectie"})
            else:
                return None
        else:
            return None

    def fetch_tagcont(self, tagline):
        """ Overused tag content fetcher, probably in bs4 as well. """
        strip = MLStripper()
        strip.feed(str(tagline))
        res = strip.get_data()
        return res