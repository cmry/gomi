__author__ = 'chris'

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def __del__(self):
        name = self.__class__.__name__
    def handle_data(self, d):
        try:
            self.fed.append(d)
        except UnicodeDecodeError:
            try:
                newd = d.decode("utf-8")
                self.fed.append(newd)
            except UnicodeDecodeError:
                newd = d.decode("iso-8859-15")
                self.fed.append(newd)
    def get_data(self):
        return ''.join(self.fed)