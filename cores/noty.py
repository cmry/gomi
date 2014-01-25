__author__ = 'chris'

import subprocess

class Notify:

    def __init__(self, namet, msg):
        self.name = namet[0][0]
        self.mail = namet[0][1]
        self.msg = msg

    def send_mail(self):
        p1 = subprocess.Popen(['echo', self.msg], stdout=subprocess.PIPE) 
        p2 = subprocess.Popen(['mail', '-s' ,"You were mentioned on IRC!", self.mail], stdin=p1.stdout)
        p1.stdout.close()
        output = p2.communicate()[0]
