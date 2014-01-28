#!/usr/bin/python
__author__ = 'chris'

from central_core.query import *
import json
import urllib

class Google:

    def __init__(self):
        self.q = Query()

    def fetch_search(self, message):
        query = self.q.search(message).split(' ')

        try:
            int(query[len(query)-1])
            amt = int(query.pop(len(query)-1))
            amt = 4 if amt > 4 else amt
        except (TypeError, ValueError):
            amt = 1

        data, outp = self.ajax(query), ''
        for x in range(0, amt):
            h = data['results'][x]
            outp += h['content'].replace('<b>', '*').replace('</b>', '*').replace('\n', '') + '\n' + \
                    '  ' + h['url'] + '\n'
        return outp.encode('utf8')

    def ajax(self, query):
        query = urllib.urlencode({'q': query})
        search_results = urllib.urlopen('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query).read()
        results = json.loads(search_results)
        return results['responseData']
