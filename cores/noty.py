__author__ = 'chris'

import subprocess


class Notify:

    def __init__(self):
        pass

    @staticmethod
    def send_mail(namet, message, log):
        name, mail, msg, log = namet[0][0], namet[0][1], '', log.push(-4)
        for x in log:
            msg += x+'\n'
        msg += message
        p1 = subprocess.Popen(['echo', msg], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['mail', '-s', "You were mentioned on IRC!", mail], stdin=p1.stdout)
        p1.stdout.close()
        output = p2.communicate()[0]
