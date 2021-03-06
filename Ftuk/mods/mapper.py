#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 30.01'

from os import getcwd
from mods import tagger
from collections import OrderedDict
from itertools import islice
from pandas import DataFrame
from re import findall
from copy import deepcopy


class Mapper(tagger.Tagger):

    def frame_map(self, data):
        """ This is just a small wrapper for pandas DataFrame. """
        return DataFrame.from_dict(data, orient='columns')

    def inf_D(self):
        """ This function pretty much resembles the D4 function from the
         Tagger, but outputs for each POS tag a list with the parentheses,
         if they were learned correctly, the GS tag and the ST tag. So we
         will get something like:
         {'sentence': ['(0,n), bool, '[tag]', '[nnnn]']} """

        D_gs, D_st = self.build_D(self.gs), self.build_D(self.struc, 'struc')  # extra dicts required for this function
        D, D2, D3 = {}, self.build_D(self.gs, 'clean'), self.build_D(self.struc, 'clean')
        errs, verrs, tlist, flist, ambs = [], [], [], [], 0   # verrs has been added for missing allignments

        #TODO: can be easily implemented in the tagger, too lazy atm though
        for K2, V2 in D2.iteritems():
            if len(V2) > 1 and not self.args['--amb']:  # skip ambiguous word
                ambs += 1
            else:
                D[K2] = list()
                for i in range(0, len(V2[0])):
                    tup = V2[0][i]
                    try:
                        if tup in D3[K2][0]:
                            D[K2].append([tup, True, D_gs[K2][0][i], D_st[K2][0][D3[K2][0].index(tup)]])
                            tlist.append(True)
                        else:
                            D[K2].append([tup, False, D_gs[K2][0][i], '[INC]']); flist.append(False)
                    except KeyError as e:   # some lines seem to be altered in wsj10.wb
                        errs.append(e)      # snippets include: LRBLCBRRBRCB, LRBLRBRRBRRB (branches?)
                    except IndexError as i:
                        verrs.append(i)


        self.logd.update({"Mapper True tags: ": len(tlist),
                          "Mapper False tags: ": len(flist),
                          "Mapper Ambiguous: ": ambs,
                          "Mapper Branch Err: ": len(errs),
                          "Mapper Tuple Err: ": len(verrs)})
        return D

    def get_D2(self):
        """ Generates an empty dictionary with all POS tags. """
        D2 = {}
        for tag in set(findall('\[[A-Z:]+.?\]', str(self.gs))):
            if tag not in D2: D2[tag] = 0  # errors in outer scope
        return D2

    def mapping(self):
        """ For the mapping, we loop through the given output file and
         when we see a certain tag number, we add it to a dictionary, and
         link it to the accompanied tag in the golden standard for the
         same key sentence. So we will get something like:
         {'[0]': {'S': n, 'NP': n, etc.}. '[1]': {idem}} """

        D, D2, inf_D = {}, self.get_D2(), self.inf_D()
        errs = []

        for key, value in inf_D.iteritems():
            for tag in value:
                if tag[3] not in D.keys():
                    D[tag[3]] = {}
                if tag[2] not in D[tag[3]] and not D[tag[3]]:
                    D[tag[3]] = deepcopy(D2)
                    try:
                        D[tag[3]][tag[2]] += 1
                    except KeyError:
                        continue
                if tag[2] in D[tag[3]]:
                    D[tag[3]][tag[2]] += 1

        if not self.args['--all']:
            del D['[INC]']

        self.logd.update({"Mapper Wrong List: ": len(errs)})
        return D

    def map_perc(self, D):
        #get the totals for each tag & for each key
        tot_dict, key_dict = self.get_D2(), {}
        for key, value in D.iteritems():
            key_dict[key] = 0
            for tag, count in value.iteritems():
                tot_dict[tag] += count
                key_dict[key] += count

        for key, value in D.iteritems():
            for tag, count in value.iteritems():
                try:
                    # TODO: still want to weight the percentages based on total
                    D[key][tag] = round(float(count)/(float(tot_dict[tag])), 4)
                    #D[key][tag] = round(float(count)/float(key_dict[key]), 4)
                except ZeroDivisionError:
                    D[key][tag] = 0.0

        return D

    def gen_map_output(self):
        D, args = self.mapping(), self.args
        if args['--perc']:
            D5 = self.map_perc(D)

        for key, value in D.iteritems():
            D[key] = sorted(value.items(),
                            key=lambda (k, v): v, reverse=True)  # removing will break the func below
            D[key] = sorted(islice(D[key], int(args['--ttop']) if args['--ttop'] else len(D[key])),
                            key=lambda (k, v): v, reverse=True)
        D5 = OrderedDict(sorted(D.items(),
                            key=lambda (k, v): v[0][1], reverse=True))
        if args['--top']:
            D5 = OrderedDict(islice(D5.iteritems(), int(args['--top'])))


        return D5

def main(args):

    # create frequency and percentage lists, edit v[0] to sort on other value >> output to latex
    corp_list = args['<input>']

    for corp in corp_list:
        mapper = Mapper(getcwd()+'/corp/'+corp, args)

        if args['--tex']:
            with open(getcwd()+'/outp/res.tex', 'w') as fl:
                fl.write("% "+corp+" ------------------------------------------------------------------------ \n")
                print "Writing tex, this might take a shitload of time, grab a coffee!"
                mapper.frame_map(mapper.gen_map_output()).to_latex(fl)
                fl.write("\n")
        else:
            print mapper.frame_map(mapper.gen_map_output()).values
        mapper.logger(mapper.logd)

if __name__ == '__main__':
    main(open(getcwd()+'/outp/log.log', 'w'))
