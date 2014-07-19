#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.07'

from crunch.grapher import Grapher
from core.util import *
import csv
import numpy as np
from copy import deepcopy
from glob import glob
from os import getcwd, remove
from os.path import isfile, isdir
from shutil import rmtree
from subprocess import call


class Classifier:

    def __init__(self, log):

        self.log = log
        self.dir = getcwd()+'/outp/'
        self.prep = None

    def route_args(self, args):
        if not args['flush']:
            func = 'kf' if args['--train'] == args['--test'] else 'tt'
            if not args['skip']:
                self.__dispatch(args, 'train', func)
                self.__dispatch(args, 'test', func)
            self.__dispatch(args, 'evaluat', func)
        else:
            conf = raw_input("Sure you want to flush (y/n): ")
            self.__flush() if conf == 'y' else exit("Aborting")

    def __dispatch(self, args, sw, func):
        """
        Following configurations are to be implemented:
        Train on Comments - Test on Comments (tenfold)
        Train on Articles - Test on Articles (tenfold)
        Train on Articles - Test on Comments (seperate)
        """

        self.log.clog.info("Starting "+sw+"ing...")
        self.prep = args['--train']+'_'+args['--source'].split('.')[0]
        self.__merge_set() if not 'article' in self.prep or 'comment' in self.prep else None
        k = 10 if not args['--kf'] else int(args['--kf'])

        if sw != 'evaluat':
            stmt = STMT(self.log, self.prep, self.dir)
            args['--mod'] = sw if sw == 'test' else args['--mod']

            if func == 'kf':
                self.__kfold(k) if sw == 'train' else None
                stmt.kfold(k, args['--mod'], args['--mem'])
            elif func == 'tt':
                stmt.route(args['--'+sw], args['--mod'], args['--mem'])
        else:
            metrics = {}
            if func == 'kf':
                for k in range(k):
                    metrics = self.__update_metrics(metrics, self.__evaluate(self.dir+self.prep+'_'+str(k)+'_fold'+'_'+args['--mod']))
            elif func == 'tt':
                metrics = self.__update_metrics(metrics, self.__evaluate(self.dir+self.prep+'_ti_'+args['--mod']))
            self.__print_metrics(metrics, k)

    def __flush(self):
        for f in glob(self.dir+'*'):
            if '_ti' not in f and '.' not in f:
                print "Removing dir: \t "+str(f)
                rmtree(f)
            if '_ti' not in f and '.' in f:
                print "Removing file: \t "+str(f)
                remove(f)

    def __merge_set(self):
        if not glob(self.dir+self.prep+'_ti.csv'):
            with open(self.dir+'comment_'+self.prep.split('_')[1]+'_ti.csv', 'r') as f1:
                with open(self.dir+'article_'+self.prep.split('_')[1]+'_ti.csv', 'r') as f2:
                        i, j = csv.reader(f1, delimiter=',', quotechar='"'), csv.reader(f2, delimiter=',', quotechar='"')
                        m, c = [], 0
                        for x in i:
                            c += 1
                            m.append(x)
                        for z in j:
                            c += 1
                            z[0] = str(c)
                            m.append(z)
            with open(self.dir+self.prep+'_ti.csv', 'ab+') as f:
                csv.writer(f, delimiter=',', quotechar='"').writerows(m)


    def __kfold(self, k):
        if isfile(self.dir+self.prep+'_'+str(k-1)+'_fold'+'_train.csv'):
            self.log.clog.warn("Folds already exist!")
        else:
            self.log.clog.info("Making foldmatrix...")
            m = [x for x in slice_list(csv_to_matrix(self.dir+self.prep+'_ti.csv', 'shuffle'), k)]
            for i in xrange(len(m)):
                self.log.clog.info("Writing fold: \t"+str(i))
                self.__write_folds(m, i)
            self.log.clog.info(str(k)+" folds have been written.")

    def __write_folds(self, m, k):
        with open(self.dir+self.prep+'_'+str(k)+'_fold'+'_train.csv', 'w') as ftrain:
            with open(self.dir+self.prep+'_'+str(k)+'_fold'+'_test.csv', 'w') as ftest:
                for i in m:
                    if m.index(i) == k:
                        csv.writer(ftest, delimiter=',', quotechar='"').writerows(i)
                    else:
                        csv.writer(ftrain, delimiter=',', quotechar='"').writerows(i)

    @staticmethod
    def __update_metrics(m, new_m, k=None):
        for key in new_m.iterkeys():
            m[key] = new_m[key] if key not in m else (m[key] + new_m[key])
        if k:
            for key in m.iterkeys():
                m[key] = m[key] / k
        return m

    def __print_metrics(self, m, k):
        l, r = [1, 3, 5, 10], self.__update_metrics(m, {}, k)
        for i in l:
            print 'map('+str(i)+'): \t' + str(round(r['map('+str(i)+')'], 3))

    def __evaluate(self, res_dir):
        # TODO: only fetch MAP for one source in the 'all' set
        # TODO: optimize memory in this function
        label_index = self.get_labi(res_dir)
        #self.graph_convergence(res_dir)
        return {'map(1)': self.mapk(self.get_reflab(res_dir), self.filter_topid(res_dir, label_index), 1),
                'map(3)': self.mapk(self.get_reflab(res_dir), self.filter_topid(res_dir, label_index), 3),
                'map(5)': self.mapk(self.get_reflab(res_dir), self.filter_topid(res_dir, label_index), 5),
                'map(10)': self.mapk(self.get_reflab(res_dir), self.filter_topid(res_dir, label_index), 10)}

    @staticmethod
    def get_labi(res_dir):
        li = list()
        with open(res_dir+'/01000/label-index.txt', 'r') as f:
            for i in f.readlines():
                li.append(i.strip('\n'))
        return li

    @staticmethod
    def get_reflab(res_dir):
        ref = glob(res_dir+'/*distributions-res.csv')[0].split('-')[0].split('/')
        ref = ref[len(ref)-1]+'.csv'
        with open(res_dir+'/../'+ref) as f:
            cf = csv.reader(f, delimiter=',', quotechar='"')
            for line in cf:
                yield line[5].split()

    @staticmethod
    def filter_topid(res_dir, li):
        for i in gen_csv(glob(res_dir+'/*distributions-res.csv')[0]):
            sort_d = {}
            for j in range(1, len(i)):
                sort_d[li[j-1]] = float(i[j]) if float(i[j]) <= 1.0 else 0.0
            yield list(sortd(sort_d, 'v', True))

    def mapk(self, actual, predicted, k=10):
        return np.mean([self.apk(a, p, k) for a, p in zip(actual, predicted)])

    @staticmethod
    def apk(actual, predicted, k=10):
        score, num_hits, predicted = 0.0, 0.0, predicted[:k] if len(predicted) > k else predicted
        for i, p in enumerate(predicted):
            if p in actual and p not in predicted[:i]:
                num_hits += 1.0
                score += num_hits / (i+1.0)
        if not actual:
            return 1.0
        return score / min(len(actual), k)

    @staticmethod
    def graph_convergence(res_dir):
        res_dir = '/home/chris/mcode/outp/article_all_ti_llda' #'/media/chris/Dump/Backup/thesis/outp/comment_all_0_fold_llda'  # for dev
        dr, l = glob(res_dir+'/0*'), []
        for i in l:
            with open(i+'/summary.txt', 'r') as f:
                l.append(f.readlines()[0].split()[1])
        Grapher.convergence_plot(l)


class STMT:

    def __init__(self, log, prep, dir):
        self.log = log
        self.prep = prep
        self.dir = dir

    def route(self, tr, mod, mem):
        self.log.slog.info(("Training" if mod != 'test' else "Testing")+" on: "+tr+'_ti.csv')
        self.edit(mod, self.prep+'_ti', tr if mod == 'test' else None)
        self.boot(mem, mod)

    def kfold(self, k, mod, mem):
        if isdir(self.dir+self.prep+'_'+str(k-1)+'_fold'+'_'+mod):
            self.log.slog.warn("Training folds already exist!")
        else:
            for k in range(k):
                self.log.slog.info("Folding"+((" "+mod) if mod == 'test' else '')+": "+str(k))
                self.edit(mod, self.prep+'_'+str(k)+'_fold')
                self.boot(mem, mod)

    def edit(self, mod, tf, tr=None):
        ifile = self.dir+'../scripts/STMT/'+mod+'.scala'
        if tf[-2:] != 'ti':
            regex_replace(ifile, self.replace('ti'), self.replace('_train', tf))
            regex_replace(ifile, self.replace(mod if mod == 'test' else 'train'), self.replace('_'+mod if mod == 'test' else '_train', tf))
            regex_replace(ifile, self.replace('llda'), self.replace('_llda', tf))
        else:
            regex_replace(ifile, self.replace(mod if mod == 'test' else 'train'), self.replace('', tf))
            regex_replace(ifile, self.replace('llda'), self.replace('_llda', tf))
            if tr:
                regex_replace(ifile, 'File\(".*'+('article' if tr != 'article' else 'comment'), 'File("'+self.dir+tr)

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

# ---------------------------------------------------

# whatever # topics per art -- all articles
# map(1): 	0.754
# map(3): 	0.84
# map(5): 	0.839
# map(10): 	0.828

# at least 1 topic per art -- all articles
# map(1): 	0.765
# map(3): 	0.85
# map(5): 	0.836
# map(10): 	0.805

# whatever # topics per art -- nu.nl articles
# map(1): 	0.807
# map(3): 	0.883
# map(5): 	0.885
# map(10): 	0.88

# at least 1 topic per art -- nu.nl articles
# map(1): 	0.792
# map(3): 	0.864
# map(5): 	0.849
# map(10): 	0.824

# whatever # topics per art -- tweakers.net articles
# map(1): 	0.723
# map(3): 	0.815
# map(5): 	0.806
# map(10): 	0.782

# at least 1 topic per art -- tweakers.net articles
# map(1): 	0.781
# map(3): 	0.87
# map(5): 	0.852
# map(10): 	0.818

# --------------------------------------------------

# at least 1 topic per art -- all comments
# map(1): 	0.373
# map(3): 	0.441
# map(5): 	0.449
# map(10): 	0.444

# at least 1 topic per art -- tweakers.net comments
# map(1):   0.433
# map(3):   0.511
# map(5):   0.517
# map(10):  0.504

# at least 1 topic per art -- nu.nl comments
# map(1):   0.371
# map(3):   0.436
# map(5):   0.443
# map(10):  0.438

# -------------------------------------------------

#           RE-TEST         all at least 1 topic p/a

# all articles -> comments
# map(1): 	0.011
# map(3): 	0.009
# map(5): 	0.01
# map(10): 	0.011

# all articles -> articles
# map(1): 	0.767
# map(3): 	0.573
# map(5): 	0.594
# map(10): 	0.616

# t.net articles -> articles
# map(1): 	0.782
# map(3): 	0.58
# map(5): 	0.602
# map(10): 	0.628

# nu.nl articles -> articles
# map(1): 	0.792
# map(3): 	0.612
# map(5): 	0.641
# map(10): 	0.659

# all comments -> comments
# map(1): 	0.373
# map(3): 	0.22
# map(5): 	0.228
# map(10): 	0.243

# t.net comments -> comments
# map(1): 	0.433
# map(3): 	0.246
# map(5): 	0.248
# map(10): 	0.267

# nu.nl comments -> comments
# map(1): 	0.371
# map(3): 	0.233
# map(5): 	0.247
# map(10): 	0.264