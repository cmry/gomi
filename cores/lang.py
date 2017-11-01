__author__ = 'chris'
__file__ = 'lang.py'

from trans import *
from re import findall

class Language:

    def __init__(self):
        pass

    def analyse_msg(self, message, sender):
        return self.jvt_lan(message, sender)

    def jvt_lan(self, message, sender):
        m = message.split(' ')
        jvt  = { 'whisky alfa':                 "Whiskey, India, Whiskey, Alfa, <name> is groen als alfalfa ",
                 'haakjes swag':                "Parkeer Alfa's man, wortel tussen kaakjes " +
                                                "Dumbell swag, zet <name> tussen haakjes",
                 'dood dimmen ' +
                 'sterf':                       "Zet me on hold, <name> doe dimmen, val even dood of dat soort dingen",
                 'machine urine':               "Nou rest in peace, <name> zwem in urine " +
                                                "Kleine shout-out naar de Machine",
                 'moeder wiepen':               "En een kleine shout-out, nee, fuck it, doe een grote "
                                                "naar <sname>'s moeder in d'r blootje, Ze is niet echt mijn type " +
                                                "hoor, maar ik zou het wel wiepen hoor",
                 'dom som ontelbaar':           "Jullie niggers zijn dommetjes, " +
                                                "dus laat me afsluiten met een sommetje, " +
                                                "Geen zorgen, ik ben snel klaar, <name> plus een is ontelbaar",
                 'formule':                     "1, 2, 3, 5, 6, Dit is de fo, de fo, de formule",
                 'een_twee':                    "Er is er geen een (2, 3), Zoals deze vier (5, 6), " +
                                                "Dus geef <name> nog een, Dit is de fo, de fo, de formule",
                 'had_je':                      "Hier is er nog een (2, 3), Van deze vier (5, 6), " +
                                                "Of had <name> al een? Dit is de fo, de fo, de formule",
                 'niveau':                      "Gaat ie lekker <name>? U ziet het zo,  Het niveau gaat opnieuw" +
                                                "omhoog, voor all y'all Ivo Niehe volk",
                 'kunstschaatsen outfit ' +
                 'schaatsen eist':              "<name> eist dingen als kunstschaatsen, Stijl sierlijk als " +
                                                "kunstschaatsen, Outfit strak als kunstschaatsen, Laat me effe " +
                                                "in je uh schaatsen",
                 'exemplaar hilarisch ' +
                 'kanarie':                     "Exemplarisch, formularisch, Een hoop lol, de vorm hilarisch, " +
                                                "Gele wervelwind, de storm kanarisch",
                 'banaan':                      "Banaan in <name>'s oor hoort het commentaar niet",
                 'jas pinpas' +
                 'drankje':                     "Jasje, dasje, pinpasje, <name>'s drankje, in het handje, " +
                                                "Buitenlandje, binnenlandje, Pimpendansje, in het Fransje",
                 'frans':                       "In het Fransje, oui oui",
                 'win':                         "<name>, goddammit nummer 1, Neem iedereen in mijn slipstream mee",
                 'element systeem':             "Het hele periodieke systeem, heeft niks op het element <name>ley",
                 'hardgaan kwardraat' +
                 'achtbaan':                    "Warpspeed hard gaan, <name> in het kwadraat, " +
                                                "op in de nacht gaan, samen in een achtbaan",
                 'oplossing':                   "De oplossing van de formule? <name> zonder scrupules"
        }

        for w in m:
            for k in jvt:
                if w in findall(r"[\w]+", k):
                    q = jvt[k].replace('<name>', sender)
                    if '<sname>' in q and 'Menno' in sender or 'Kobus' in sender:
                        return
                    else:
                        return q.replace('<sname>', sender)
