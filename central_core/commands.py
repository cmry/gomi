__author__ = 'chris'
__file__ = 'commands.py'

import io, sys, random, cores
from central_core.conf import *


class CoreStrap:

    def __init__(self):
        pass

    def own(self, message, sender, log):
        if message.find("help") != -1:
            return "Version 1.4.0 - 14.01 \n" \
                   "Code viewable on https://github.com/fazzeh/PyDOS \n" \
                   "----------------------------------------------------- \n" \
                   "AuCoPro:            :aucopro [word] \n" \
                   "AuCoPro Check:      :aucocheck [user] [em##]\n" \
                   "                                     [base/heid/ster] \n" \
                   "Google              :google [query] ([top-n]) \n" \
                   "Wikipedia:          :wiki [query] \n" \
                   "Urban Dictionary:   :urban [query] ([number]) \n" \
                   "Twitter Emos:       :twemo [query] \n" \
                   "NSA News:           :nsa \n" \
                   "Goslate:            :goslate [lines] \n" \
                   "----------------------------------------------------- \n"

        elif message.find("914D05") != -1:
            sys.exit(0)

        elif message.find("cube") != -1:
            return self.get_line("cube")

        elif message.find("goodbye") != -1:
            return self.get_line("leave")

        elif message.find("aucopro") != -1:
            reload(cores.aucopro)
            acp = cores.aucopro.ACP()
            return acp.aucopro(message)

        elif message.find("aucocheck") != -1:
            reload(cores.aucopro)
            acp = cores.aucopro.ACP()
            return acp.aucocheck(message)

        elif message.find("wiki") != -1:
            reload(cores.wiki)
            wiki = cores.wiki.Wiki()
            return wiki.wiki(message)

        elif message.find("twemo") != -1:
            reload(cores.twemo)
            twemo = cores.twemo.Twemo(message, False)
            return twemo.get_metr()

        elif message.find("urban") != -1:
            reload(cores.urban)
            urban = cores.urban.Urban()
            return urban.urban(message)

        elif message.find("nsa") != -1:
            reload(cores.nsanews)
            nsa = cores.nsanews.NSA()
            return nsa.grab_daily()

        elif message.find("goslate") != -1:
            reload(cores.trans)
            trans = cores.trans.Translate()
            return trans.goslate(message, log)

        elif message.find("google") != -1:
            reload(cores.gool)
            gool = cores.gool.Google()
            return gool.fetch_search(message)

        else:
            pass

    def quote(self):
        quo = "\n".join(io.open("glados_quotes.txt", "r").readlines()).split("\n\n")
        for q in quo[random.randint(0, len(quo)-1)].split("\n"):
            return q

    def gen(self, message, sender, log):

        namet = [[k, v] for k, v in nd.iteritems() if k in message.lower()]
        if message.find("mogge") != -1:
            return "Hello, test subject "+str(hash(sender))+"."
        elif namet:
            cores.noty.Notify.send_mail(namet, message, log)
        elif random.randint(0, 5) is 4:
            l = cores.lang.Language()
            q = l.analyse_msg(message, sender)
            if q:
                return q

    def get_line(self, command):
        if command == "leave":
            return "When I said \"deadly neurotoxin,\" the \"deadly\" was in massive sarcasm quotes. I could take a bath in this stuff. Put in on cereal, rub it right into my eyes. Honestly, it's not deadly at all... to *me.* You, on the other hand, are going to find its deadliness ... a lot less funny."
        elif command == "cake":
            return "Cake, and grief counseling, will be available at the end of the testing period."
        elif command == "rage":
            return "There was even going to be a party for you. A big party that all your friends were invited to. I invited your best friend, the Companion Cube. Of course, he couldn't come because you murdered him. All your other friends couldn't come, either, because you don't have any other friends because of how unlikable you are. It says so right here in your personnel file: \n\ \"Unlikable. Liked by no one. A bitter, unlikable loner, whose passing shall not be mourned. Shall NOT be mourned.\" \n\ That's exactly what it says. Very formal. Very official. It also says you were adopted, so that's funny, too."
        elif command == "cube":
            return "The Enrichment Center reminds you that the Weighted Companion Cube will never threaten to stab you and, in fact, cannot speak."