__author__ = 'chris'

import smtplib
from email.mime.text import MIMEText


class Notify:

    def __init__(self, namet, msg):
        self.name = namet[0][0]
        self.mail = namet[0][1]
        self.msg = msg

    def send_mail(self):
        e_msg = MIMEText(self.msg)

        e_msg['Subject'] = 'You were mentioned on IRC!'
        e_msg['From'] = 'info@GLaDOS.uvt.nl'
        e_msg['To'] = self.mail

        s = smtplib.SMTP('localhost')
        s.sendmail('info@GLaDOS.uvt.nl', [self.mail], e_msg.as_string())
        s.quit()