#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 30.01'

from os import getcwd
from mods import tagger
from re import sub, match


class Mapper(tagger.Tagger):

    def mapping(self):
        """ For the mapping, we loop through the given output file and
         when we see a certain tag number, we add it to a dictionary, and
         link it to the accompanied tag in the golden standard for the
         same key sentence. So we will get something like:
         {'0': {'S': n, 'NP': n, etc.}. '1': {idem}}
        """

        D_gs, D_st, D4 = self.build_D(self.gs), self.build_D(self.struc, 'struc'), self.build_D4()

        for key, value in D_st.iteritems():
            print value

def main(args):

    # create frequency and percentage lists, edit v[0] to sort on other value >> output to latex
    corp_list = args['<input>']

    for corp in corp_list:
        mapper = Mapper(getcwd()+'/corp/'+corp, args)
        mapper.mapping()


        #D, klist, labels = mapper.gen_output()

        # if args['--tex']:
        #     with open(getcwd()+'/outp/res.tex', 'w') as fl:
        #         fl.write("% "+corp+" ------------------------------------------------------------------------ \n")
        #         tagger.frame_ord(D.values(), klist, labels).to_latex(fl)
        #         fl.write("\n")
        # else:
        #     print tagger.frame_ord(D.values(), klist, labels).values
        # tagger.logger(tagger.logd)

if __name__ == '__main__':
    main(open(getcwd()+'/outp/log.log', 'w'))
