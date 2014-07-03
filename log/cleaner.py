__author__ = 'chris'

from glob import glob
from re import sub

class Janitor:

    def __init__(self):
        self.logs = list()
        self.__build_loglist()
        self.logs = self.__wipe()

    def __build_loglist(self):
        for fl in glob("*.log"):
            with open(fl, 'r') as f:
                l = [sub('   *', '  ', x).split('  ') for x in f.readlines()]
                for i in range(0, len(l)):
                    p = l[i][0].split(' ')
                    l[i].remove(l[i][0])
                    l[i] = p + l[i]
                for x in l:
                    self.logs.append(x)

    def __wipe(self):
        newlog = []
        for i in self.logs:
            count = 0
            for x in i:
                if 'Go atom!' in x:
                    break
                elif 'Boomer ticker' in x:
                    break
                elif 'Event loop' in x:
                    break
                elif 'Closed control' in x:
                    break
                elif 'WARN' in x:
                    break
                elif 'already in log' in x:
                    break
                else:
                    count += 1
            if count == len(i):
                newlog.append(i)
        return newlog

    def get_clean(self):
        with open('clean_log.log', 'ab+') as f:
            for line in self.logs:
                f.write('\t'.join(line))

if __name__ == '__main__':
    cl = Janitor()
    cl.get_clean()