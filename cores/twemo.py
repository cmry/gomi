__author__ = 'chris'
__file__ = 'twemo.py'

import re
import codecs
from twitter import *
from collections import Counter
from main.query import *


class Twemo:

    def __init__(self, term, until_date):

        self.q = Query()
        self.term = self.q.search(term)

        self.until_date = until_date

        self.hap = [":)", ":-)", ":-D", ":D", "^^", "^_^", "8-)"]
        self.jau = [":F", "xD", "x)", ":p", ":P", ":3"]
        self.sar = [":')"]
        self.sad = [":(", ":((", ":-(", ":'(", ":'-("]
        self.ang = [":@", ":-@"]
        self.con = [":s", ":S"]
        self.cyn = [":x", ";x", "-_-", "-_-'"]

        self.emodict = {}

        self.access_token        = "622784277-xz0Nurl7bhMvTD3fbr08fXAv5cWPl4rspt4zxVfW"
        self.access_token_secret = "mzCuyzucCUWZQM4gzIp4F2RLanp7qPEJRLggTILBHmk"
        self.consumer_key        = "l8RZHdwP7wxuOb25AUUkg"
        self.consumer_secret     = "TNWxdbhdIpQLs80pdblklpEH2JjIhQTU8J1TJap94c"

        self.bigdatar = 'res.txt'
        self.texts = self.grab_texts(self.term, until_date)


    def grab_texts(self, term, until_date):
        api = self.create_twitter_api()
        query = self.restrict_date(term, until_date)
        result = self.twitter_search_all(api, self.conjunction([query, self.disjunction(self.hap + self.jau + self.sar + self.sad + self.ang + self.con + self.cyn)]))
        texts = (tweet['text'] for tweet in result)
        return texts


    def get_wordlink(self, emo, am):
        self.emodict['hap'] = []
        self.emodict['jau'] = []
        self.emodict['sar'] = []
        self.emodict['sad'] = []
        self.emodict['ang'] = []
        self.emodict['con'] = []
        self.emodict['cyn'] = []
        self.matchwords(codecs.open(self.bigdatar, 'r', 'utf-8'))
        for word, count in self.get_count(self.emodict[emo], am):
            return '%s: %7d' % (word, count)


    def get_wc(self, am):
        for word, count in self.get_count(self.bigdatar, am):
            return '%s: %7d' % (word, count)

    def get_metr(self):
        (hapc, jauc, sarc, sadc, angc, conc, cync) = self.pos_neg_counts()
        return("Metrics for {7}: \n happy: {0} \n jaunty: {1} \n sarcastic: {2} \n sad: {3} \n angry: {4} \n confused: {5} \n cynical: {6}".format(hapc, jauc, sarc, sadc, angc, conc, cync, self.term))

    def disjunction(self, sl):
        """Join strings in sl with OR."""
        return " OR ".join(sl)


    def conjunction(self, terms):
        """Join strings in terms with spaces."""
        return " ".join(terms)


    def restrict_date(self, term, until_date=None):
        """Optionally add until:DATE keywords to query."""
        if until_date:
            return "{0} until: {1}".format(term, until_date)
        else:
            return term

    def create_twitter_api(self):
        """Create and return an authenticated instance of Twitter API."""
        return Twitter(auth=OAuth(self.access_token, self.access_token_secret, self.consumer_key, self.consumer_secret))

    def find_min_id(self, dl):
        res = min(i['id'] for i in dl)
        return res

    def re_disjunction(self, sl):
        res, stack = [], []
        for i in sl:
            for j in i:
                stack.append(re.escape(j))
            if stack:
                res.append(''.join(stack)); stack = []
        return "|".join(res)

    def pos_neg_counts(self):
        """Searches for occurences of terms in pos and terms in neg in
        each of the texts and return a tuple of how many pos matches and neg
        matches were found. """
        hap, jau, sar = self.re_disjunction(self.hap), self.re_disjunction(self.jau), self.re_disjunction(self.sar)
        sad, ang, con = self.re_disjunction(self.sad), self.re_disjunction(self.ang), self.re_disjunction(self.con)
        cyn = self.re_disjunction(self.cyn)

        hapc, jauc, sarc, sadc, angc, conc, cync = 0, 0, 0, 0, 0, 0, 0

        for t in self.texts:
            if re.search(hap,t):
                hapc += 1
            if re.search(jau,t):
                jauc += 1
            if re.search(sar,t):
                sarc += 1
            if re.search(sad,t):
                sadc += 1
            if re.search(ang,t):
                angc += 1
            if re.search(con,t):
                conc += 1
            if re.search(cyn,t):
                cync += 1

        return (hapc, jauc, sarc, sadc, angc, conc, cync)

    def sanitize(self, t):
        pattern = re.compile('[\W_]+')
        t = [x.lower() for x in t]
        t = [pattern.sub('', x) for x in t]
        t = filter(None, t)
        return t

    def matchwords(self, target):
        for line in target:
            t = line.split(' ')
            if set(t) & set(self.hap):
                self.emodict['hap'].extend(t)
            if set(t) & set(self.jau):
                self.emodict['jau'].extend(t)
            if set(t) & set(self.sar):
                self.emodict['sar'].extend(t)
            if set(t) & set(self.sad):
                self.emodict['sad'].extend(t)
            if set(t) & set(self.ang):
                self.emodict['ang'].extend(t)
            if set(t) & set(self.con):
                self.emodict['con'].extend(t)
            if set(t) & set(self.cyn):
                self.emodict['cyn'] = str(word for word in t)

    def get_count(self, target, am):
        corpus = []
        try:
            with codecs.open(target, 'r', 'utf-8') as fl:
                for line in fl:
                    corpus.extend(line.split())
        except Exception:
            corpus = target

        corpus = list(set(corpus))
        corpus = self.sanitize(corpus)

        counter = Counter()
        for word in corpus:
            counter[word] += 1

        return counter.most_common(am)

    def twitter_search_all(self, api, query, max_id=None):
        '''Run query on twitter and yield each tweet from from
        all the result pages.'''
        if max_id:
            r = api.search.tweets(q=query, count=100, max_id=max_id)
        else:
            r = api.search.tweets(q=query, count=100)
        if len(r.get('statuses', [])) == 0:
            if False:
                yield
        else:
            min_id = self.find_min_id(r['statuses'])
            for tweet in r['statuses']:
                yield tweet
            for tweet in self.twitter_search_all(api, query, max_id=min_id-1):
                yield tweet