#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 04.07'

from core.util import *
import csv
from copy import deepcopy
from os import getcwd
from subprocess import call


class Classifier:

    def __init__(self, log):

        self.log = log
        self.dir = getcwd()+'/outp/'
        self.prep = None

    def route_args(self, args):
        if args['--train'] == args['--test']:
            self.__dispatch(args, 'train', 'kf')
            self.__dispatch(args, 'test', 'kf')
        else:
            self.__dispatch(args, 'train', 'tt')
            self.__dispatch(args, 'test', 'tt')

    def __dispatch(self, args, mod, func):
        if mod == 'train':
            Trainer(self.log).train(args, func)
        elif mod == 'test':
            Tester(self.log).test(args, func)


class Trainer(Classifier):

    def train(self, args, func):
        """
        Following configurations are to be implemented:
        Train on Comments - Test on Comments (tenfold)
        Train on Articles - Test on Articles (tenfold)
        Train on Articles - Test on Comments (seperate)
        """

        self.log.trlog.info("Starting training...")
        self.prep = args['--train']+'_'+args['--source']
        stmt = STMT(self.log, self.prep, self.dir)

        if func == 'kf':
            k = 10 if not args['--kf'] else int(args['--kf'])
            self.kfold(k)
            stmt.kfold(k, args['--mod'], args['--mem'])
        elif func == 'tt':
            stmt.train(args['--train'], args['--mod'], args['--mem'])

    def kfold(self, k):
        m = [x for x in slice_list(csv_to_matrix(self.dir+self.prep+'_ti.csv'), k)]
        for i in xrange(len(m)):
            self.__write_folds(m, i)
        self.log.trlog.info(str(k)+" folds have been written.")

    def __write_folds(self, m, k):
        train = [deepcopy(m).pop(k)]
        assert len(train) < len(m)
        with open(self.dir+self.prep+'_'+str(k)+'_fold'+'_train.csv', 'w') as fp:
            csv.writer(fp, delimiter=',', quotechar='"').writerows([x for i in train for x in i])
        with open(self.dir+self.prep+'_'+str(k)+'_fold'+'_test.csv', 'w') as fp:
            csv.writer(fp, delimiter=',', quotechar='"').writerows([x for i in m for x in i])


class Tester(Classifier):

    def test(self, args, func):

        self.log.telog.info("Starting testing...")
        if func == 'kf':
            pass


class STMT:

    def __init__(self, log, prep, dir):
        self.log = log
        self.prep = prep
        self.dir = dir

    def train(self, tr, mod, mem):
        self.log.slog.info("Training on: "+tr+'_ti.csv')
        self.edit(mod, self.prep+'_ti')
        self.boot(mem, mod)

    def kfold(self, k, mod, mem):
        for k in range(k):
            self.log.slog.info("Folding: "+str(k))
            self.edit(mod, self.prep+'_'+str(k)+'_fold')
            self.boot(mem, mod)

    def edit(self, mod, tf):
        ifile = self.dir+'../scripts/STMT/'+mod+'.scala'
        if tf[-2:] != 'ti':
            regex_replace(ifile, self.replace('ti'), self.replace('_train', tf))
            regex_replace(ifile, self.replace('train'), self.replace('_train', tf))
            regex_replace(ifile, self.replace('llda'), self.replace('_llda', tf))
        else:
            regex_replace(ifile, self.replace('train'), self.replace('', tf))
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