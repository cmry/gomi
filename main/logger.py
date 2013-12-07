__author__ = 'chris'
__file__ = 'logger.py'

class Log:

    def __init__(self):
        self.stack = []

    def feed(self, message):
        if len(self.stack) is 5:
            self.stack.pop(0)
        if len(self.stack) < 5:
            self.stack.append(message)

    def push(self):
        return self.stack