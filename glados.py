import irclib
import sys
import io
import random
import time
from commands import *


class IRCCat(irclib.SimpleIRCClient):

    def __init__(self, target):
        irclib.SimpleIRCClient.__init__(self)
        self.target = target
        self.quotes = "\n".join(io.open("glados_quotes.txt","r").readlines()).split("\n\n")

    def on_welcome(self, connection, event):
        if irclib.is_channel("#"+self.target):
            connection.join("#"+self.target)
            self.target="#"+self.target
        else:
            self.send_it()

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def on_pubmsg(self, connection, event):
        cmd = CmdStrap()
        message, sender = event.arguments()[0], event.source()[0:event.source().find("!")]
        print sender + ": " + message

        if message.find("glados") != -1 or message.find("GLaDOS") != -1:
            self.talk(self.cmd.own(message, sender)) if self.cmd.own(message, sender) is not 'pass' else self.talk(self.quote())
        elif message.find("cake") != -1:
            self.talk(self.cmd.get_line("cake"))
        else:
            self.talk(self.cmd.gen(message, sender)) if self.cmd.gen(message, sender) else time.sleep(1)


    def talk(self, msg):
        if isinstance(msg, str):
            msg = str(msg)
            for l in msg.split("\n"):
                self.connection.privmsg(self.target, l)
        else:
            for l in msg:
                self.connection.privmsg(self.target, l)

    def quote(self):
        for q in self.quotes[random.randint(0,len(self.quotes)-1)].split("\n"):
            return q

    def leave(self):
        self.connection.quit(self.get_line("leave"))

def main():

    try:
        with open('ch.txt', 'r') as fl:
            inf = fl.read().split(' ')
        lab = IRCCat(inf[0])

        try:
            lab.connect(inf[1], 6667, 'GLaDOS')
        except irclib.ServerConnectionError, x:
            print x
            sys.exit(1)

        lab.start()
    except Exception as e:
        print e

if __name__ == "__main__":
    main()
