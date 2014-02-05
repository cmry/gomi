#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.02'


class Timer:
    """ Class to properly parse and return the dates in our
    dataset. Works with {'Article_dates': {}, 'Comment_dates': {}}. """

    def time_docs(self, timeline, doc):
        #first we split and process the data for the articles and count
        art_date = self.parse_date(doc)

        if art_date not in timeline['Article_dates'].keys():
            timeline['Article_dates'][art_date] = 1
        else:
            timeline['Article_dates'][art_date] += 1

        return timeline

    def time_comms(self, timeline, cmt):
        #then we want to do the same for all the dates in our comments
        cmt_date = self.parse_date(cmt, 'comment_')

        if cmt_date not in timeline['Comment_dates'].keys():
            timeline['Comment_dates'][cmt_date] = 1
        else:
            timeline['Comment_dates'][cmt_date] += 1

        return timeline

    def parse_date(self, jdoc, prep=str()):
        # TODO: this part might have to be changed due to date format
        try:
            date = jdoc[prep+'date'].split()
            return str(self.parse_day(date[0]) + "/" + self.parse_month(date[1]) + "/" +
                       jdoc[prep+'year'])  # + " " + jdoc['time']) <-- uncomment for time
        except IndexError:
            return 'UNK'

    def parse_day(self, day):
        if int(day) < 10:
            day = "0"+day
        return day

    def parse_month(self, date):
        datel = {
            'januari':      '01',
            'februari':     '02',
            'maart':        '03',
            'april':        '04',
            'mei':          '05',
            'juni':         '06',
            'juli':         '07',
            'augustus':     '08',
            'september':    '09',
            'oktober':      '10',
            'november':     '11',
            'december':     '12'
        }
        return datel[date.lower()]