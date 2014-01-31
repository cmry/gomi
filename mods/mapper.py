#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 30.01'

from os import getcwd
from mods import tagger
from re import sub, match


class Mapper(tagger.Tagger):

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
                            D[K2].append([tup, True, D_gs[K2][0][i], D_st[K2][0][D3[K2][0].index(tup)]]); tlist.append(True)
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

    def plus_tag(self, D, tag):
        if tag[3] not in D:
            D[tag[3]] = {}
        if tag[2] not in D[tag[3]]:
            D[tag[3]][tag[2]] = 0
            D[tag[3]][tag[2]] += 1
        else:
            D[tag[3]][tag[2]] += 1
        return D

    def mapping(self):
        """ For the mapping, we loop through the given output file and
         when we see a certain tag number, we add it to a dictionary, and
         link it to the accompanied tag in the golden standard for the
         same key sentence. So we will get something like:
         {'[0]': {'S': n, 'NP': n, etc.}. '[1]': {idem}} """

        D, inf_D = {}, self.inf_D()
        errs = []

        for key, value in inf_D.iteritems():
            try:
                for tag in value:
                    if self.args['--all']:
                        if tag[1]:
                            D = self.plus_tag(D, tag)
                    else:
                        D = self.plus_tag(D, tag)
            except IndexError as e:
                errs.append(e)

        self.logd.update({"Mapper Wrong List: ": len(errs)})

        return D

def main(args):

    # create frequency and percentage lists, edit v[0] to sort on other value >> output to latex
    corp_list = args['<input>']

    for corp in corp_list:
        mapper = Mapper(getcwd()+'/corp/'+corp, args)
        D, klist, labels = mapper.gen_output(mapper.mapping())

        if args['--tex']:
            with open(getcwd()+'/outp/res.tex', 'w') as fl:
                fl.write("% "+corp+" ------------------------------------------------------------------------ \n")
                mapper.frame_ord(D.values(), klist, labels).to_latex(fl)
                fl.write("\n")
        else:
            print mapper.frame_ord(D.values(), klist, labels).values
        mapper.logger(mapper.logd)

if __name__ == '__main__':
    main(open(getcwd()+'/outp/log.log', 'w'))
