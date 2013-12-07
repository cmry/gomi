__author__ = 'chris'
__file__ = 'glados.py'

import irclib
import sys
from time import sleep
from main.conf import *
from main.commands import *


class IRCCat(irclib.SimpleIRCClient):

    def __init__(self, chl):
        """ Initializing the class, setting up the channel from conf """
        irclib.SimpleIRCClient.__init__(self)
        self.tag = chl

    def on_welcome(self, con, evt):
        """ Used for joining, can't be simplified or talk function will break. """
        if irclib.is_channel("#"+self.tag):
            con.join("#"+self.tag)
            self.tag = "#"+self.tag
        else:
            self.send_it()

    def on_pubmsg(self, con, evt):
        """ Generates command list, needed to reload alterations on the fly.
            Also handles pushing commands and reactions through decision tree. """
        try:
            cmd = CmdStrap()
            message, sender = evt.arguments()[0], evt.source()[0:evt.source().find("!")]
            if message.lower().find("glados") != -1:
                self.talk(cmd.own(message, sender))
            else:
                self.talk(cmd.gen(message, sender)) if cmd.gen(message, sender) else sleep(1)
            del cmd
        except Exception as e:
            #prevent disconnects due to crappy programming
            self.talk("The cake is a lie."); print e

    def talk(self, msg):
        """ Simple privmsg command, make sure talk msg are strings!!! """
        for l in msg.split("\n"):
            self.connection.privmsg(self.tag, l)

    def on_disconnect(self, con, evt):
        """ On disconnect, try reloading. Not working? """
        main()

def main():
    server = IRCCat(cl)
    try:
        server.connect(sn, p, bn)
        print "Oh... It's you. It's been a long time. How have you been? \n" \
              "I've been really busy being dead. You know, after you MURDERED ME."
    except irclib.ServerConnectionError, x:
        sys.exit(1)
    server.start()

if __name__ == "__main__":
    main()
