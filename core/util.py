__author__ = 'chris'
__version__ = '09.07'

import csv
from re import sub
from random import shuffle

def regex_replace(f, needle, rock):
    with open(f, 'r') as rf:
        stack = sub(needle, rock, rf.read())
    with open(f, 'w') as wf:
        wf.write(stack)


def csv_to_matrix(csvf, shuf=False):
    with open(csvf, 'r') as f:
        cf = csv.reader(f)
        m = [[x for x in row] for row in cf]
        shuffle(m) if shuf else None
        return m


def slice_list(l, k):
    i = 0
    for x in xrange(k):
        j = i + len(l[x::k])
        yield l[i:j]
        i = j
