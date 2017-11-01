__author__ = 'chris'

import subprocess
import time
from core.logger import Logger


class Automata:

    def __init__(self):

        self.l = Logger()
        self.l.alog.info("Go atom!")

        #3776668 recent 3630000 old
        #up to 3776668 done, 2910000 old start

        i, j = 2000000, 2910000 #i, j = 3776668, 3779959
        step = (j - i) / 80  # nu.nl
        #step = 96081 / 50
        self.stepl = [x for x in range(i, j+step, step)]  # nu.nl
        #self.stepl = [x for x in range(0, 96081+step, step)]
        self.booter()

    def booter(self):
        proc = [x for x in self.stacker()]
        self.boomer()
        self.terminator(proc)
        time.sleep(60)

    def boomer(self):
        boom, tick = 3600, 0
        while boom > 0:
            time.sleep(1)
            boom -= 1; tick += 1
            # if tick == 30:
            #     self.l.alog.info("Boomer ticker...................................................................")
            #     tick = 0
        self.l.alog.warning("BOOM!")

    def stacker(self):
        for x in range(0, len(self.stepl)-1):
            time.sleep(10)
            proc = subprocess.Popen(["python", "aivb.py", "scrape", "-n",
                                     "--min="+str(self.stepl[x]), "--max="+str(self.stepl[x+1]),
                                     "--intv=0",
                                     "--check", '--radar'])
            yield proc
        self.l.alog.info("Stacker is queued, setting boomer...")

    def terminator(self, i):
        for x in i:
            subprocess.Popen.terminate(x)
        self.l.alog.info("Killed processes, going to sleep...")

if __name__ == '__main__':
    atom = Automata()
    while True:
        atom.booter()
