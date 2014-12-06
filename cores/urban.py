__author__ = 'chris'

from urllib2 import urlopen
from central_core.query import *


class Urban:

    def __init__(self):
        """ Old module, did some code improvement, not written with OOP
        in mind though. Moreover, its a very crude solution, should use bs4. """
        self.q = Query()

    def grab_def(self, data):
        def_raw, def_list = "", []
        concat, record = False, True
        divcount = 0

        for line in data.split():
            if divcount is 2:
                definition = ""
                def_raw = def_raw.replace('<div class="example">', '\n\n').replace(" class='definition'", '')
                for character in def_raw:
                    if character is "<":
                        record = False
                    elif character is ">":
                        record = True
                    elif not record:
                        continue
                    else:
                        definition += character
                def_list.append(definition.replace("&#39;", "'").replace("&quot;", '"'))
                divcount, concat, def_raw = 0, False, ""

            elif line.startswith("class='definition'") or concat:
                def_raw += (" "+line)
                concat = True
                if "</div>" in line:
                    divcount += 1
            else:
                continue

        return def_list

    def urban(self, message):
        q = self.q.search(message).split(' ')
        def_nr = int(q[len(q)-1]) if len(q) > 1 else 0
        if def_nr is not 0:
            q.remove(q[len(q)-1])
        q = '%20'.join(q)

        def_list = self.grab_def(urlopen('http://www.urbandictionary.com/define.php?term='+q).read())

        if def_list:
            try:
                return self.q.cut(def_list[def_nr])
            except IndexError:
                return "Corrupted cores! We're in luck."
        else:
            return "Corrupted cores! We're in luck."
