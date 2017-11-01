__author__ = 'chris'
__file__ = 'aucopro.py'

import re
import pysftp
from urllib2 import urlopen
from central_core.query import *
from central_core.conf import *


class ACP:

    def __init__(self):
        """ Old, very specific module, ugly coding, useless for anything
        other than itself. Better not touch any further or will break. """
        self.q = Query()
        self.inf = ftpl

    def aucocheck(self, message):
        message, srv = message.split(), pysftp.Connection(self.inf[0], username=self.inf[1], password=self.inf[2])
        user, em, mode = message[2], message[3], message[4]

        if mode is "base":
            result = srv.execute('sh annotation/chris/done/check.sh annotation/'+user+'/done/'+em)
            output = ""
            for line in result:
                output += line

        elif mode is "heid" or mode is "ster":
            if mode is "heid":
                word_list = srv.execute('cat annotation/'+user+'/done/'+em+" | grep '[a-z]heid$' | grep +")
            elif mode is "ster":
                srv.execute('cat annotation/'+user+'/done/'+em+" | grep '[a-z]ster$' | grep + > ster.txt")
                srv.execute('cat annotation/'+user+'/done/'+em+" | grep '[a-z]er$' | grep + > er.txt")
                srv.execute("grep -v -E '^(af|aan|achter|af|bij|binnen|boven|buiten|door|in|langs|met|na|naar|om|onder|op|over|rond|te|tegen|ten|ter|tussen|uit|van|vanaf|voor|voorbij)' ster.txt > ster2.txt")
                srv.execute("grep -v -E '^(af|aan|achter|af|bij|binnen|boven|buiten|door|in|langs|met|na|naar|om|onder|op|over|rond|te|tegen|ten|ter|tussen|uit|van|vanaf|voor|voorbij)' er.txt > er2.txt")
                srv.execute('rm ster.txt')
                srv.execute('rm er.txt')
                word_list_ster = srv.execute('cat ster2.txt')
                word_list_er = srv.execute('cat er2.txt')
                srv.execute('rm ster2.txt')
                srv.execute('rm er2.txt')
            try:
                word_list
            except NameError:
                try:
                    word_list_ster
                    word_list_er
                except NameError:
                    return "Corrupted cores! We're in luck!"
                else:
                    words = ""
                    for line in word_list_ster:
                        words += line
                    for line in word_list_er:
                        words += line
                    output = self.aucompare(words, 'ster', 'er')
            else:
                words = ""
                for line in word_list:
                    words += line

                output = self.aucompare(words, 'heid', 'heid')
        else:
            return "Invalid mode"

        if len(output) == 0:
            return "All is good."
        else:
            return output

    def aucompare(self, words, key1, key2):
        words = words.replace('+', '\n').split('\n')
        output = ""
        for line in words:
            if line.endswith(key1) or line.endswith(key2):
                url = 'http://www.woorden.org/index.php?woord=' + line
                usock = urlopen(url)
                data = usock.read()
                usock.close()
                if "woord komt ook niet voor in de woordenlijsten die zijn goedgekeurd door de Taalunie" in data:
                    output += line+"\n"
                else:
                    continue
            else:
                continue
        return output

    def aucopro(self, message):

        key = self.q.search(message)

        if len(key) < 3:
            return "You are making this harder than it needs to be."

        srv = pysftp.Connection(self.inf[0], username=self.inf[1], password=self.inf[2])

        if '+' in key or '_' in key:
                result = (srv.execute('grep '+key+' annotation/*/done/em*'))
        else:
            srv.execute('cat annotation/*/done/em* | sed s/\[\+\_]//g | grep -n '+key+" | cut -d':' -f1 > annotation/chris/done/count.txt")
            times = srv.execute('cat annotation/chris/done/count.txt | wc -l')
            times = int(re.sub('\n','',times[0]))
            result = []
            while times != 0:
                line = srv.execute('grep "$(cat annotation/*/done/em* | sed `cat annotation/chris/done/count.txt | sed'+" '"+str(times)+"!d'`'!d'"+')" annotation/*/done/em*')
                for entry in line:
                    result.append(entry)
                times -= 1

        result = list(set(result))
        result.sort()
        srv.execute('rm annotation/count.txt')
        srv.execute('exit')

        if len(result) == 0:
                    return "Oh, sorry. I'm cleaning out the test chambers."
        else:
            output = ''
            for line in result:
                line = re.sub('annotation/','',line)
                line = re.sub('/done/',' - ',line)
                line = re.sub(':',': ',line)
                output += line
            if len(output) == 0:
                return "You are making this harder than it needs to be."
            else:
                return output
