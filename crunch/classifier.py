#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.07'

from core.util import *
import csv
from copy import deepcopy
from glob import glob
from os import getcwd
from os.path import isfile, isdir
from subprocess import call


class Classifier:

    def __init__(self, log):

        self.log = log
        self.dir = getcwd()+'/outp/'
        self.prep = None

    def route_args(self, args):
        func = 'kf' if args['--train'] == args['--test'] else 'tt'
        if not args['skip']:
            self.__dispatch(args, 'train', func)
            self.__dispatch(args, 'test', func)
        self.__dispatch(args, 'evaluat', func)

    def __dispatch(self, args, sw, func):
        """
        Following configurations are to be implemented:
        Train on Comments - Test on Comments (tenfold)
        Train on Articles - Test on Articles (tenfold)
        Train on Articles - Test on Comments (seperate)
        """

        self.log.clog.info("Starting "+sw+"ing...")
        self.prep = args['--train']+'_'+args['--source']
        k = 10 if not args['--kf'] else int(args['--kf'])

        if sw != 'evaluat':
            stmt = STMT(self.log, self.prep, self.dir)
            args['--mod'] = sw if sw == 'test' else args['--mod']

            if func == 'kf':
                self.__kfold(k) if sw == 'train' else None
                stmt.kfold(k, args['--mod'], args['--mem'])
            elif func == 'tt':
                stmt.route(args['--train'], args['--mod'], args['--mem'])
        else:
            if func == 'kf':
                for k in range(k):
                    self.__evaluate(self.dir+self.prep+'_'+str(k)+'_fold'+'_'+args['--mod'])
            elif func == 'tt':
                self.__evaluate(self.dir+self.prep+'_'+args['--mod'])

    def __kfold(self, k):
        if isfile(self.dir+self.prep+'_'+str(k-1)+'_fold'+'_train.csv'):
            self.log.clog.warn("Folds already exist!")
        else:
            m = [x for x in slice_list(csv_to_matrix(self.dir+self.prep+'_ti.csv', 'shuffle'), k)]
            for i in xrange(len(m)):
                self.__write_folds(m, i)
            self.log.clog.info(str(k)+" folds have been written.")

    def __write_folds(self, m, k):
        train = deepcopy(m)
        test = [train.pop(k)]
        assert len(train) < len(m)
        with open(self.dir+self.prep+'_'+str(k)+'_fold'+'_train.csv', 'w') as fp:
            csv.writer(fp, delimiter=',', quotechar='"').writerows([x for i in train for x in i])
        with open(self.dir+self.prep+'_'+str(k)+'_fold'+'_test.csv', 'w') as fp:
            csv.writer(fp, delimiter=',', quotechar='"').writerows([x for i in test for x in i])

    def __evaluate(self, res_dir):
        label_index = self.get_labi(res_dir)
        d = self.filter_topid(res_dir, label_index)
        r = self.get_reflab(res_dir)
        p1, p5, pk = self.ref_comp(d, r, label_index)
        self.log.clog.info("\n Precision at 1: \t " + str(p1) + "\n Precision at 5: \t " + str(p5) + "\n Precision at k: \t " + str(pk))

    def ref_comp(self, d, r, li):
        cong = [[0 for _ in li] for _ in li]
        p1, p5, pk = 0.0, 0.0, 0.0
        for key in d.iterkeys():
            gs, temp_p5, temp_pk = r[key].split(), 0.0, 0.0
            k = len(gs)
            for i in xrange(k if k > 5 else 5):
                if list(d[key])[i] in gs:
                    if i <= 0:
                        p1 += 1.0
                    if i <= 5-1:
                        temp_p5 += 1.0
                    if i <= k-1:
                        temp_pk += 1.0
            p5 += (temp_p5/float(len(gs) if len(gs) < 5 else 5))
            pk += (temp_pk/float(len(gs)))
        return p1/len(d), p5/len(d), pk/len(d)

    def get_reflab(self, res_dir, li=list()):
        ref = glob(res_dir+'/*distributions-res.csv')[0].split('-')[0].split('/')
        ref = ref[len(ref)-1]+'.csv'
        r = {}
        with open(res_dir+'/../'+ref) as f:
            cf = csv.reader(f, delimiter=',', quotechar='"')
            for line in cf:
                index, topics = line[0], line[5]
                r[index] = topics
        return r

    def get_labi(self, res_dir, li=list()):
        with open(res_dir+'/01000/label-index.txt', 'r') as f:
            for i in f.readlines():
                li.append(i.strip('\n'))
        return li

    def filter_topid(self, res_dir, li):
        d = csv_to_matrix(glob(res_dir+'/*distributions-res.csv')[0])
        m = {}
        for i in xrange(len(d)):
            sort_d = {}
            for j in xrange(len(d[i])):
                #if 0.1 <= float(d[i][j]) <= 1:  # big assumption here
                sort_d[li[j-1]] = float(d[i][j])
            m[d[i][0]] = sortd(sort_d, 'v', True)
        return m


class STMT:

    def __init__(self, log, prep, dir):
        self.log = log
        self.prep = prep
        self.dir = dir

    def route(self, tr, mod, mem):
        self.log.slog.info(("Training" if mod != 'test' else "Testing"+" on: ")+tr+'_ti.csv')
        self.edit(mod, self.prep+'_ti')
        self.boot(mem, mod)

    def kfold(self, k, mod, mem):
        if isdir(self.dir+self.prep+'_'+str(k-1)+'_fold'+'_'+mod):
            self.log.slog.warn("Training folds already exist!")
        else:
            for k in range(k):
                self.log.slog.info("Folding"+((" "+mod) if mod == 'test' else '')+": "+str(k))
                self.edit(mod, self.prep+'_'+str(k)+'_fold')
                self.boot(mem, mod)

    def edit(self, mod, tf):
        ifile = self.dir+'../scripts/STMT/'+mod+'.scala'
        if tf[-2:] != 'ti':
            regex_replace(ifile, self.replace('ti'), self.replace('_train', tf))
            regex_replace(ifile, self.replace(mod if mod == 'test' else 'train'), self.replace('_'+mod if mod == 'test' else '_train', tf))
            regex_replace(ifile, self.replace('llda'), self.replace('_llda', tf))
        else:
            regex_replace(ifile, self.replace(mod if mod == 'test' else 'train'), self.replace('_'+mod if mod == 'test' else '_train', tf))
            regex_replace(ifile, self.replace('llda'), self.replace('_llda', tf))

    def replace(self, pof, tf=None):
        return 'ile\(".*_'+pof if not tf else 'ile("'+self.dir+tf+pof

    def boot(self, mem, mod):
        """
        Make sure that this directory exists and that
        tmt-0.4.0.jar is in the exact same folder, mcode
        is a symbolic link to the code folder.
        """
        call(["java", "-Xmx"+mem+"m", "-jar",
              self.dir+"../scripts/STMT/tmt-0.4.0.jar",
              self.dir+"../scripts/STMT/"+mod+".scala"])