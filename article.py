__author__ = 'chris'
import json

class Article:

    def __init__(self, logger):
        self.log = logger
        """ This class is used to form a decent structure for JSON
        storage of articles, elements are defined by this project.
        Structure:
        {
            "article": {
                "id": "extraction number"
                "source": "t.net / nu.nl"
                "nr": "article number"
                "date": "date"
                "year": "year"
                "time": "time"
                "subjects": "subject 1, subject 2, etc"
                "content": {
                        "title": "title",
                        "intro": "introduction",
                        "text": "text"
                },
                "comments": [
                    {   "id": "id",
                        "user": "user name",
                        "date": "date",
                        "year": "year",
                        "time": "time",
                        "text": "text",
                        "vote": "vote nr"
                    },
                    {   "id": "id",
                        "user": "user name",
                        "date": "date",
                        "year": "year",
                        "time": "time",
                        "text": "text",
                        "vote": "vote nr",
                    }
                ]
            }
        }
        """
        self.article = {}

        self.id = 0
        self.source = ''
        self.nr = 0
        self.date = ''
        self.year = 0
        self.time = ''
        self.subj = ''

        self.content = {'title': '',
                        'intro': '',
                        'text': ''}

        self.comments = []
        self.comment = {'comment_id': '',
                        'comment_user': '',
                        'comment_date': '',
                        'comment_year': '',
                        'comment_time': '',
                        'comment_text': '',
                        'comment_vote': ''}

    def __str__(self):
        return json.dumps(self.article,
                          sort_keys=False,
                          indent=4,
                          separators=(',', ': '))

    def struc_article(self):
        """ Inserts all collected items into the dictionary """
        self.article['id'] = self.id
        self.article['source'] = self.source
        self.article['nr'] = self.nr
        self.article['date'] = self.date
        self.article['year'] = self.year
        self.article['time'] = self.time
        self.article['subjects'] = self.subj
        self.article['content'] = self.content
        self.article['comments'] = self.comments
        '''with open('res/'+str(self.article['id'])+'.txt', 'w') as f:
            f.write(json.dumps(self.article,
                               sort_keys=False,
                               indent=4, ensure_ascii=False,
                               separators=(',', ': ')))

            self.log.rlog.info(self.article['source'] +
                               " article: " +
                               self.article['content']['title'] +
                               " saved to " +
                               str(self.article['id']) +
                               ".")'''
        print json.dumps(self.article, sort_keys=False, indent=4, separators=(',', ': '))