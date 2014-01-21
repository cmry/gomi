#!/usr/bin/env python

__author__ = 'chris'

from re import sub, findall
from pandas import DataFrame
from collections import OrderedDict
from os import getcwd
import sys

class Tagger:

    def __init__(self, struc, args):
        """ This class extracts the required information from the gs file
            and given results (struc) files and wsj length, and calculates
            the scores for correctly learned POS tags. FTUK! """

        self.args = args
        self.col = self.get_col()

        # cut longer than wsj(x) variable
        self.gs, tgs = [], open(getcwd()+'/corp/wsj_menno.gold.fix3.txt', 'r').readlines()
        for line in tgs:
            if len(line.split(' @@@ ')[0].split(' ')) <= args['--wsjlen']:
                self.gs.append(line)

        # output files do not contain spaces, fix for cc.py
        self.struc, tstruc = [], open(struc, 'r').readlines()
        for line in tstruc:
            if not line.startswith('#'):
                self.struc.append(line.replace(')', ') ').replace(',', ', '))

        self.logger({"Method: ":          str(struc).replace(getcwd()+'/corp/wsj10.', ''),
                     "Total GS items: ":  len(self.gs),
                     "Total ST items: ":  len(self.struc)})

    def logger(self, logd):
        for message, value in logd.iteritems():
            count = 19
            while count >= len(message):
                message += "\t"
                count -= 3
            print ("%s %s" % (message, value))

    def frame_ord(self, data, r, c):
        return DataFrame(data, index=r, columns=c)

    def build_D(self, fl, clean=None):
        """ Dick 1 is a dictionary with the GS words as keys and a list
            of possible assigned POS tags (more entries = ambigious)
            will look like {'Mom': ['[NP][NNP]', '[NP]']}.

            Dick 2 is a dictionary with the GS words as key and a list
            of the structures with the POS tags removed. Will look like:
            {'Mom': [ '(0, 1)(0, 2)' ]}, so tuple values.

            Dick 3 is a dictionary with the STR words as key and a list
            of the structures with the POS numbers removed. Will look same
            as D2, for tuple value comparison. """

        D = {}
        for line in fl:
            parts = line.split(' @@@ ')
            parts[0] = parts[0].replace(', ', ',')  # correct fuckup in cc.py
            if clean:
                #remove POS tags and space between 'tuples' for D2 and D3
                parts[1] = sub(', \[[A-Z0-9, ]*.\]', '', parts[1])
                parts[1] = sub(', ', ',', parts[1])
            else:
                #only keep the POS tags for D1
                parts[1] = sub('[(0-9),]', '', parts[1])
                parts[1] = sub('   ', ' ', parts[1])[2:]  # [2:] corrects ws

            if parts[0] in D:  # and therefore ambiguous
                D[parts[0]].append(parts[1].split(' '))
            else:
                D[parts[0]] = list()
                D[parts[0]].append(parts[1].split(' '))
        return D

    def build_D4(self):
        """ Dick 4 is an inbetween dictionary of Dick 2 and Dick 3, which
            will have the common words as key and a list/vector of correctly
            structured indexes as values. So for example: {'Mom': [True, False,
            False, True]}. """

        D, D2, D3 = {}, self.build_D(self.gs, 'clean'), self.build_D(self.struc, 'clean')
        errs, tlist, flist, ambs = [], [], [], 0
        for K2, V2 in D2.iteritems():
            if len(V2) > 1 and not self.args['--amb']:  # skip ambiguous word
                ambs += 1
            else:
                D[K2] = list()
                for tup in V2[0]:
                    try:
                        if tup in D3[K2][0]:
                            D[K2].append(True)
                            tlist.append(True)
                        else:
                            D[K2].append(False)
                            flist.append(False)
                    except KeyError as e:
                        # some lines seem to be altered in wsj10.wb
                        # snippets include: LRBLCBRRBRCB, LRBLRBRRBRRB (branches?)
                        errs.append(e)

        self.logger({"True tags: ": len(tlist),
                     "False tags: ": len(flist),
                     "Ambiguous: ": ambs,
                     "Branch Err: ": len(errs)})
        return D

    def build_D5(self):
        """ Dick 5 is the result dictionary of Dick 4 and Dick 1, which
            includes all the POS tags and a True, False and Total score. """

        # the --cor --tot --inc parameters should still be implemented here!

        D = {}
        for line in self.gs:
            tags = findall('\[[A-Z\$]+\]', line)
            for tag in tags:
                if tag not in D:
                    D[tag] = [0, 0]  # D[tag] = [0, 0, 0]

        D1, D4 = self.build_D(self.gs), self.build_D4()
        errs, checkl = [], []
        for K1, V1 in D1.iteritems():
            try:
                V4 = D4[K1]
                checkl.append(V4)
                for i in range(0, len(V4)-1):  # -1 to ignore \n
                    if V4[i]:
                        D[V1[0][i]][0] += 1
                    #else:
                        #D[V1[0][i]][1] += 1
                    D[V1[0][i]][1] += 1  # should be [2]
            except KeyError as e:
                #"Estimated volume was a moderate 3.5 million ounces" seems to
                # error for some reason
                errs.append(e)

        self.logger({"Misc errors: ": len(errs),
                     "Total sentences GS: ": len(D1),
                     "Total sentences ST: ": len(D4),
                     "Seen items: ": len(checkl)})
        return D

    def get_col(self, c={}):
        for a, b in self.args.iteritems():
            if findall('--(cor|inc|tot)$', a) and b:
                c[a] = b
        return OrderedDict(sorted(c.items(), key=lambda (k, v): k, reverse=False))

    def perc_D5(self, D5, tot=0):
        for K5, V5 in D5.iteritems():
            try:
                if ('--tot' in self.col and '--inc' in self.col) or ('--tot' in self.col and '--cor' in self.col):
                    tot = int([sum(i) for i in zip(*D5.values())][len(self.col)-1])
                    D5[K5].append(round(float(D5[K5][0]) / float(tot), 4))
                    if '--cor' in self.col:
                        D5[K5].append(round(float(D5[K5][self.col.keys().index('--cor')])
                                            / float(D5[K5][len(self.col)-1]), 4))
                    if '--inc' in self.col:
                        D5[K5][1] = round(float(D5[K5][self.col.keys().index('--inc')])
                                          / float(D5[K5][len(self.col)-1]), 4)
                else:
                    exit("ERROR: Percentage of what?!")

            except ZeroDivisionError:
                for i in range(0, len(D5[K5])):
                    D5[K5][i] = 0.0

        self.logger({"Total structs GS: ": tot,
                     "-------------------------": ""})
        return D5

    def gen_output(self):
        labels, args = ['correct', 'total', '% correct', '% correct of total'], self.args
        if args['--perc'] and not args['--ngr']:
            M = self.perc_D5(OrderedDict(sorted(self.build_D5().items(), key=lambda (k, v): v[0], reverse=True)))
        elif not args['--perc'] and args['--ngr']:
            M = None
        elif args['--perc'] and args['--ngr']:
            M = None
        else:
            M = self.build_D5()
            del labels[-2]

        D5 = OrderedDict(sorted(M.items(), key=lambda (k, v): v[0], reverse=True))

        klist = []
        for tag in D5.keys():
            tag = tag.replace('[', '\[')
            tag = tag.replace(']', '\]')
            klist.append(tag)
        return D5, klist, labels


def main(args):

    with open(getcwd()+'/outp/res.tex', 'w') as fl:
        #create frequency and percentage lists, edit v[0] to sort on other value >> output to latex
        corp_list = args['<input>']

        for corp in corp_list:
            fl.write("% "+corp+" ------------------------------------------------------------------------ \n")
            tagger = Tagger(getcwd()+'/corp/'+corp, args)

            D5P, klist, labels = tagger.gen_output()
            tagger.frame_ord(D5P.values(), klist, labels).to_latex(fl)

            fl.write("\n")

if __name__ == '__main__':
    main(open(getcwd()+'/outp/log.log', 'w'))
