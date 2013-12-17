__author__ = 'chris'
__file__ = 'lang.py'

from trans import *
from re import findall

class Language:

    def __init__(self):
        pass

    def analyse_msg(self, message, sender):
        #t = Translate()
        #trans = t.goslate(message, sender)
        return self.jvt_lan(message, sender)

    def jvt_lan(self, message, sender):
        m = message.split(' ')
        jvt  = { 'whisky alfa':                 "Whiskey, India, Whiskey, Alfa \n <name> is groen als alfalfa ",
                 'haakjes swag':                "Parkeer Alfa's man, wortel tussen kaakjes \n" +
                                                "Dumbell swag, zet <name> tussen haakjes",
                 'dood dimmen ' +
                 'sterf':                       "Zet me on hold, <name> doe dimmen, val even dood of dat soort dingen",
                 'machine urine':               "Nou rest in peace, <name> zwem in urine \n" +
                                                "Kleine shout-out naar de Machine",
                 'moeder wiepen':            "En een kleine shout-out, nee, fuck it, doe een grote \n"
                                                "naar <sname>'s moeder in d'r blootje \n Ze is niet echt mijn type " +
                                                "hoor, maar ik zou het wel wiepen hoor",
                 'dom som ontelbaar':           "Jullie niggers zijn dommetjes, " +
                                                "dus laat me afsluiten met een sommetje \n" +
                                                "Geen zorgen, ik ben snel klaar, <name> plus een is ontelbaar",
                 'formule':                     "1, 2, 3, 5, 6 \n Dit is de fo, de fo, de formule",
                 'een_twee':                    "Er is er geen een (2, 3), \n Zoals deze vier (5, 6) \n" +
                                                "Dus geef <name> nog een \n Dit is de fo, de fo, de formule",
                 'had_je':                      "Hier is er nog een (2, 3) \n Van deze vier (5, 6) \n" +
                                                "Of had <name> al een? \n Dit is de fo, de fo, de formule",
                 'niveau':                      "Gaat ie lekker <name>? U ziet het zo \n Het niveau gaat opnieuw" +
                                                "omhoog \n voor all y'all Ivo Niehe volk",
                 'kunstschaatsen outfit ' +
                 'schaatsen eist':              "<name> eist dingen als kunstschaatsen \n Stijl sierlijk als " +
                                                "kunstschaatsen \n Outfit strak als kunstschaatsen \n Laat me effe " +
                                                "in je uh schaatsen",
                 'exemplaar hilarisch ' +
                 'kanarie':                     "Exemplarisch, formularisch \n Een hoop lol, de vorm hilarisch \n" +
                                                "Gele wervelwind, de storm kanarisch",
                 'banaan':                      "Banaan in <names>'s oor hoort het commentaar niet",
                 'jas das pinpas' +
                 'drankje':                     "Jasje, dasje, pinpasje \n <names>'s drankje, in het handje \n" +
                                                "Buitenlandje, binnenlandje \n Pimpendansje, in het Fransje",
                 'win':                         "<name>, goddammit nummer 1 \n Neem iedereen in mijn slipstream mee",
                 'element systeem':             "Het hele periodieke systeem \n heeft niks op het element <name>ley",
                 'hardgaan kwardraat' +
                 'achtbaan':                    "Warpspeed hard gaan, <name> in het kwadraat, \n" +
                                                "op in de nacht gaan, samen in een achtbaan",
                 'oplossing':                   "De oplossing van de formule? \n <name> zonder scrupules"
        }

        for w in m:
            for k in jvt:
                if w in findall(r"[\w]+", k):
                    q = jvt[k].replace('<name>', sender)
                    if '<sname>' in q and sender is 'Menno' or sender is 'Kobus':
                        return
                    else:
                        return q.replace('<sname>', sender)