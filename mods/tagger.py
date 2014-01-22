#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 22.01'

from re import sub, findall
from pandas import DataFrame
from collections import OrderedDict
from os import getcwd


class Tagger:

    def __init__(self, struc, args):
        """ This class extracts the required information from the gs file
            and given results (struc) files and wsj length, and calculates
            the scores for correctly learned POS tags. """

        self.args = args
        self.col = self.get_col()
        self.logd = {}

        # cut longer than wsj(x) variable
        self.gs, tgs = [], open(getcwd()+'/corp/wsj_menno.gold.fix3.txt', 'r').readlines()
        for line in tgs:
            if len(line.split(' @@@ ')[0].split(' ')) <= int(args['--wsjlen']):
                self.gs.append(line)

        # output files do not contain spaces, fix for cc.py
        self.struc, tstruc = [], open(struc, 'r').readlines()
        for line in tstruc:
            if not line.startswith('#'):
                self.struc.append(line.replace(')', ') ').replace(',', ', '))

        self.logd.update({"Method: ":          str(struc).replace(getcwd()+'/corp/wsj10.', ''),
                          "Total GS items: ":  len(self.gs),
                          "Total ST items: ":  len(self.struc)})

    def logger(self, logd):
        """ Used for displaying some metrics determined by a long-ass
            OCD list. Accepts a dict with metric names and values and
            formats them so they look neat in terminal. """

        order = {k: v for v, k in enumerate(['Method: ', 'Total GS items: ', 'Total ST items: ', 'True tags: ',
                                             'False tags: ', 'Ambiguous: ', 'Branch Err: ', 'Misc Err: ',
                                             'Total sents GS: ', 'Total sents ST: ', 'Seen items: ',
                                             'Total structs GS: ', '--------------------------'])}
        logd = OrderedDict(sorted(logd.items(), key=lambda i: order.get(i[0])))
        for message, value in logd.iteritems():
            message += " "*(22-len(message)-len(str(value))+len(str(min(logd.values()))))
            print ("%s %s" % (message, value))

    def frame_ord(self, data, r, c):
        """ This is just a small wrapper for pandas DataFrame. """
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
        # TODO: might want to refactor this function with rexeg
        for line in fl:
            parts = line.split(' @@@ ')
            parts[0] = parts[0].replace(', ', ',')  # correct fuckup in cc.py
            if clean:
                # remove POS tags and space between 'tuples' for D2 and D3
                parts[1] = sub(', \[[A-Z0-9, ]*.\]', '', parts[1])
                parts[1] = sub(', ', ',', parts[1])
            else:
                # only keep the POS tags for D1
                parts[1] = sub('[(0-9),]', '', parts[1])
                parts[1] = sub('   ', ' ', parts[1])[2:]  # [2:] corrects ws

            if parts[0] in D:  # and therefore ambiguous
                D[parts[0]].append(parts[1].split(' '))
            else:
                D[parts[0]] = list()  # do not refactor or function will break, idiot
                D[parts[0]].append(parts[1].split(' '))
        return D

    def build_D4(self):
        """ Dick 4 is an in-between dictionary of Dick 2 and Dick 3, which
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
                            D[K2].append(True); tlist.append(True)
                        else:
                            D[K2].append(False); flist.append(False)
                    except KeyError as e:   # some lines seem to be altered in wsj10.wb
                        errs.append(e)      # snippets include: LRBLCBRRBRCB, LRBLRBRRBRRB (branches?)

        self.logd.update({"True tags: ": len(tlist),
                          "False tags: ": len(flist),
                          "Ambiguous: ": ambs,
                          "Branch Err: ": len(errs)})
        return D

    def build_D5(self, top=None):
        """ Dick 5 is the result dictionary of Dick 4 and Dick 1, which
            includes all the POS tags and optionally a Correct, Incorrect
            and Total score. These can be altered by the CLI. """

        D, D1, D4 = {}, self.build_D(self.gs), self.build_D4()
        errs, checkl = [], []

        if not self.args['--ngr']:
            for tag in set(findall('\[[A-Z\$]+]', str(self.gs))):
                if tag not in D: D[tag] = [0 for _ in self.col]  # errors in outer scope ><
        else:
            for v in D1.itervalues():
                for tag in range(0, len(v)):
                    try:
                        n = ' '.join(v[0][tag-int(self.args['--ngr']):tag])
                        if n not in D and '\n' not in n: D[n] = [0 for _ in self.col]
                    except KeyError:
                        continue

        for K1, V1 in D1.iteritems():
            try:
                V4 = D4[K1]
                checkl.append(V4)
                for i in range(0, len(V4)-1):  # -1 to ignore \n
                    if not self.args['--ngr']:
                        if V4[i] and '--cor' in self.col:
                            D[V1[0][i]][self.col.keys().index('--cor')] += 1
                        elif '--inc' in self.col:
                            D[V1[0][i]][self.col.keys().index('--inc')] += 1
                        if '--tot' in self.col:
                            D[V1[0][i]][self.col.keys().index('--tot')] += 1
                    else:
                        if V4[i-int(self.args['--ngr']):i].count(True) is 2 and '--cor' in self.col and self.args['--ngr']:
                            D[' '.join(V1[0][i-int(self.args['--ngr']):i])][self.col.keys().index('--cor')] += 1
                        elif '--inc' in self.col:
                            D[' '.join(V1[0][i-int(self.args['--ngr']):i])][self.col.keys().index('--inc')] += 1
                        if '--tot' in self.col:
                            D[' '.join(V1[0][i-int(self.args['--ngr']):i])][self.col.keys().index('--tot')] += 1
            except KeyError as e:
                # "Estimated volume was a moderate 3.5 million ounces" seems to
                # error for some reason
                errs.append(e)

        if self.args['--ngr']:
            klist = []
            [klist.append(k) for k in D.iterkeys() if len(k.split(' ')) < int(self.args['--ngr'])]
            for k in klist:
                del D[k]

        # TODO: add only list n-top items
        #vlist = []
        #[vlist.append(self.col.keys().index('--tot')) for v in D.itervalues()]
        # for i in sorted(vlist):

        self.logd.update({"Misc Err: ": len(errs),
                          "Total sents GS: ": len(D1),
                          "Total sents ST: ": len(D4),
                          "Seen items: ": len(checkl)})
        return D

    def get_col(self, c={}):
        """ Small wrapper function to check cor/inc/tot argument presence. """
        for a, b in self.args.iteritems():
            if findall('--(cor|inc|tot)$', a) and b: c[a] = b
        return OrderedDict(sorted(c.items(), key=lambda (k, v): k, reverse=False))

    def perc_D5(self, D5, tot=0):
        for K5, V5 in D5.iteritems():
            try:
                if ('--tot' in self.col and '--inc' in self.col) or ('--tot' in self.col and '--cor' in self.col):
                    if '--cor' in self.col:
                        D5[K5].append(round(float(D5[K5][self.col.keys().index('--cor')])
                                            / float(D5[K5][len(self.col)-1]), 4))
                    if '--inc' in self.col:
                        D5[K5].append(round(float(D5[K5][self.col.keys().index('--inc')])
                                          / float(D5[K5][len(self.col)-1]), 4))
                    tot = int([sum(i) for i in zip(*D5.values())][len(self.col)-1])
                    D5[K5].append(round(float(D5[K5][0]) / float(tot), 4))
                else:
                    exit("ERROR: Percentage of what?!")
            except ZeroDivisionError:
                for i in range(0, len(D5[K5])):
                    D5[K5].append(0.0)

        self.logd.update({"Total structs GS: ": tot,
                          "--------------------------": ""})

        for key, value in D5.iteritems():
            print value
        return D5

    def gen_output(self):
        M, labels, args = self.build_D5(), [], self.args

        [labels.append(k[2:]) for k in self.col.keys()]; [labels.append('% '+k[2:]) for k in self.col.keys()]
        sortk = self.col.keys().index('--'+args['--sortk']) if not args['--perc'] else \
                self.col.keys().index('--'+args['--sortk'])+len(self.col)

        if args['--perc']:
            M = self.perc_D5(OrderedDict(sorted(M.items(), key=lambda (k, v): v[0], reverse=True)))
        else:
            labels = labels[:-len(self.col.keys())]

        D5 = OrderedDict(sorted(M.items(), key=lambda (k, v): v[sortk], reverse=True))
        klist = [tag.replace('$', '\$').replace('[', '$\lbrack$').replace(']', '$\rbrack$') for tag in D5.keys()]
        return D5, klist, labels


def main(args):

    # create frequency and percentage lists, edit v[0] to sort on other value >> output to latex
    corp_list = args['<input>']

    for corp in corp_list:
        tagger = Tagger(getcwd()+'/corp/'+corp, args)
        D, klist, labels = tagger.gen_output()

        if args['--tex']:
            with open(getcwd()+'/outp/res.tex', 'w') as fl:
                fl.write("% "+corp+" ------------------------------------------------------------------------ \n")
                tagger.frame_ord(D.values(), klist, labels).to_latex(fl)
                fl.write("\n")
        else:
            print tagger.frame_ord(D.values(), klist, labels).values
        tagger.logger(tagger.logd)

if __name__ == '__main__':
    main(open(getcwd()+'/outp/log.log', 'w'))
