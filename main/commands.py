__author__ = 'chris'
__file__ = 'commands.py'

import io
import random
from sys import exit

from cores.twemo import *
from cores.wiki import *
from cores.urban import *
from cores.aucopro import *
from cores.nsanews import *

class CmdStrap:

    def own(self, message, sender):

        if message.find("help") != -1:
            return "Version 1.2.0 - 13.12 \n" \
                   "Code viewable on https://github.com/fazzeh/PyDOS \n" \
                   "AuCoPro: \t\t\t glados aucopro [word] \n" \
                   "AuCoPro Check: \t\t glados aucocheck [user] [em##]\n \t\t\t\t\t [base/heid/ster] \n" \
                   "Wikipedia: \t\t\t glados wiki [query] \n" \
                   "Urban Dictionary: \t glados urban [query] ([number]) \n" \
                   "Twitter Emos: \t\t glados twemo [query] \n" \
                   "NSA News: \t\t\t glados nsa \n"

        elif message.find("914D05") != -1:
            exit(0)

        elif message.find("cube") != -1:
            return self.get_line("cube")

        elif message.find("goodbye") != -1:
            return self.get_line("leave")

        elif message.find("aucopro") != -1:
            acp = ACP()
            return acp.aucopro(message)

        elif message.find("aucocheck") != -1:
            acp = ACP()
            return acp.aucocheck(message)

        elif message.find("wiki") != -1:
            wiki = Wiki()
            return wiki.wiki(message)

        elif message.find("twemo") != -1:
            twemo = Twemo(message, False)
            return twemo.get_metr()
        
        elif message.find("urban") != -1:
            urban = Urban()
            return urban.urban(message)

        elif message.find("nsa") != -1:
            nsa = NSA()
            return nsa.grab_daily()
        
        else:
            return self.quote()

    def quote(self):
        quo = "\n".join(io.open("../cores/glados_quotes.txt", "r").readlines()).split("\n\n")
        for q in quo[random.randint(0, len(quo)-1)].split("\n"):
            return q

    def gen(self, message, sender):
        if message.find("mogge") != -1:
            return "Hello, test subject "+str(hash(sender))+"."

    def get_line(self, command):
        if command == "leave":
            return "When I said \"deadly neurotoxin,\" the \"deadly\" was in massive sarcasm quotes. I could take a bath in this stuff. Put in on cereal, rub it right into my eyes. Honestly, it's not deadly at all... to *me.* You, on the other hand, are going to find its deadliness ... a lot less funny."
        elif command == "cake":
            return "Cake, and grief counseling, will be available at the end of the testing period."
        elif command == "rage":
            return "There was even going to be a party for you. A big party that all your friends were invited to. I invited your best friend, the Companion Cube. Of course, he couldn't come because you murdered him. All your other friends couldn't come, either, because you don't have any other friends because of how unlikable you are. It says so right here in your personnel file: \n\ \"Unlikable. Liked by no one. A bitter, unlikable loner, whose passing shall not be mourned. Shall NOT be mourned.\" \n\ That's exactly what it says. Very formal. Very official. It also says you were adopted, so that's funny, too."
        elif command == "cube":
            return "The Enrichment Center reminds you that the Weighted Companion Cube will never threaten to stab you and, in fact, cannot speak."
