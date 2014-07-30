#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.07'

from core.util import *
from crunch.evaluator import Evaluator
from crunch.dater import Dater
import csv
from glob import glob
from os import remove
from os.path import isfile, isdir
from shutil import rmtree
from subprocess import call


class Classifier:

    def __init__(self, log):

        self.log = log
        self.dir = '/home/chris/mbup/'  # getcwd()+'/outp/'
        self.prep = None

    def route_args(self, args):
        if not args['flush']:
            func = 'kf' if args['--train'] == args['--test'] else 'tt'
            if not args['eval'] and not args['dater']:
                self.__dispatch(args, 'train', func)
                self.__dispatch(args, 'test', func)
            elif args['eval']:
                self.__dispatch(args, 'evaluat', func)  # placed here due to error
            else:
                self.__dispatch(args, 'dump', func)
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

        if sw != 'evaluat' and sw != 'dump':
            stmt = STMT(self.log, self.prep, self.dir)
            args['--mod'] = sw if sw == 'test' else args['--mod']

            if func == 'kf':
                self.__kfold(k) if sw == 'train' else None
                stmt.kfold(k, args['--mod'], args['--mem'])
            elif func == 'tt':
                stmt.route(args['--'+sw], args['--mod'], args['--mem'])
        elif sw == 'evaluat':
            Evaluator(func, self.dir+self.prep, args['--mod'], k if func == 'kf' else 0)
        else:
            Dater(func, self.dir+self.prep, args['--mod'], k if func == 'kf' else 0)

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