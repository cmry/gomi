#!/usr/bin/python
__author__ = 'chris'

from main.query import *
import json
import urllib

class Google:

    def __init__(self):
        self.q = Query()

    def fetch_search(self, message):
        query = self.q.search(message).split(' ')
        amt = query.pop(len(query)-1) if isinstance(query[len(query)-1], int) else len(query)-1
        data = self.ajax(query)

        hits = data['results']
        tot = 'Total results: %s' % data['cursor']['estimatedResultCount']
        top = 'Top %d hits:' % amt

        outp = top + '                    ' + tot + '\n'
        for x in range(0, amt):
            h = data['results'][x]
            outp += h['title'].replace('<b>', '*').replace('</b>', '*') + ' -- ' + \
                    h['content'].replace('<b>', '*').replace('</b>', '*').replace('\n', '') + '\n' + \
                    '  ' + h['url'] + '\n'
        return outp.encode('utf8')

    def ajax(self, query):
        query = urllib.urlencode({'q': query})
        search_results = urllib.urlopen('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query).read()
        results = json.loads(search_results)
        return results['responseData']
