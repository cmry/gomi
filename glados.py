from irclib import *
import sys
from time import sleep
from conf import *
from commands import *


class IRCCat(SimpleIRCClient):

    def __init__(self, chl):
        SimpleIRCClient.__init__(self)
        self.tag = chl

    def on_welcome(self, con, evt):
        if is_channel("#"+self.tag):
            con.join("#"+self.tag)
        else:
            self.send_it()

    def on_pubmsg(self, con, evt):
        cmd = CmdStrap()
        message, sender = evt.arguments()[0], evt.source()[0:evt.source().find("!")]
        if message.lower().find("glados") != -1:
            self.talk(cmd.own(message, sender))
        else:
            self.talk(cmd.gen(message, sender)) if cmd.gen(message, sender) else sleep(1)

    def talk(self, msg):
        for l in msg.split("\n"):
            self.connection.privmsg(self.tag, l)

    def on_disconnect(self, con, evt):
        main()

def main():
    server = IRCCat(cl)
    try:
        server.connect(sn, p, bn)
    except ServerConnectionError, x:
        print x
        sys.exit(1)
    server.start()

if __name__ == "__main__":
    main()
