__author__ = 'chris'
__file__ = 'logger.py'


class Log:

    def __init__(self):
        self.stack = []

    def feed(self, message, sender):
        if len(self.stack) is 50:
            self.stack.pop(0)
        if len(self.stack) < 50:
            self.stack.append(sender+': '+message)

    def push(self, amt):
        return self.stack[amt:]
