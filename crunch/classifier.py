#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.07'

from crunch.evaluator import Evaluator
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
            metrics = {}
            if func == 'kf':
                for k in range(k):
                    metrics = self.__update_metrics(metrics, self.__evaluate(self.dir+self.prep+'_'+str(k)+'_fold'+'_'+args['--mod']))
            elif func == 'tt':
                metrics = self.__update_metrics(metrics, self.__evaluate(self.dir+self.prep+'_'+args['--mod']))
            self.__print_metrics(metrics, k)

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

    def __update_metrics(self, m, new_m, k=None):
        print k
        for key in new_m.iterkeys():
            m[key] = new_m[key] if key not in m else (m[key] + new_m[key])
            if k:
                m[key] = m[key] / k
        return m

    def __print_metrics(self, m, k):
        l, r = [1, 3, 5, 10], self.__update_metrics(m, {}, k)
        for i in l:
            print 'map('+str(i)+'): \t' + str(round(r['map('+str(i)+')'], 3))

    def __evaluate(self, res_dir):
        label_index = self.get_labi(res_dir)
        d, r = self.filter_topid(res_dir, label_index), self.get_reflab(res_dir)
        M, inf = self.annotate(d, r, len(label_index))
        ev, res, conf = Evaluator(M, inf), [], []
        for i in range(0, len(M)):
            q = 'q'+str(i+1)
            res.append([ev.precision(q), ev.recall(q), ev.f_measure(1.0, q), ev.accuracy(q)])
        return {'map(1)': ev.map(1), 'map(3)': ev.map(3), 'map(5)': ev.map(5), 'map(10)': ev.map(10)}

    @staticmethod
    def get_reflab(res_dir):
        ref = glob(res_dir+'/*distributions-res.csv')[0].split('-')[0].split('/')
        ref = ref[len(ref)-1]+'.csv'
        r = {}
        with open(res_dir+'/../'+ref) as f:
            cf = csv.reader(f, delimiter=',', quotechar='"')
            for line in cf:
                index, topics = line[0], line[5]
                r[index] = topics
        return r

    @staticmethod
    def get_labi(res_dir):
        li = list()
        with open(res_dir+'/01000/label-index.txt', 'r') as f:
            for i in f.readlines():
                li.append(i.strip('\n'))
        return li

    @staticmethod
    def filter_topid(res_dir, li):
        d = csv_to_matrix(glob(res_dir+'/*distributions-res.csv')[0])
        m = {}
        for i in xrange(len(d)):
            sort_d = {}
            for j in xrange(len(d[i])):
                #if 0.1 <= float(d[i][j]) <= 1:  # big assumption here
                sort_d[li[j-1]] = float(d[i][j])
            m[d[i][0]] = sortd(sort_d, 'v', True)
        return m

    @staticmethod
    def annotate(d, r, tot):
        M, inf, j = [], {'tot': tot}, 0
        for key in d.iterkeys():
            j += 1
            gs_tags, out_tags = r[key].split(), list(d[key])
            inf['q'+str(j)] = len(gs_tags)
            M.append(['R' if out_tags[i] in gs_tags else 'N' for i in xrange(len(out_tags))])
        return M, inf


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