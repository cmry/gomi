#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'chris'
__version__ = 'Version 26.06'

import logging
import os
from crunch.compresser import Compresser

class Logger:

    def __init__(self):
        """ Logger class to display and record operations and errors.
         Options:

        #logger.debug('debug message')
        #logger.info('info message')
        #logger.warn('warn message')
        #logger.error('error message')
        #logger.critical('critical message') """

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=os.getcwd()+'/log/'+str(hash(self))+'.log',
                            filemode='w')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        self.alog = logging.getLogger('atom')
        self.rlog = logging.getLogger('scraper')
        self.nlog = logging.getLogger('nu.nl')
        self.tlog = logging.getLogger('tweakers')
        self.elog = logging.getLogger('core')
        self.llog = logging.getLogger('loader')
        self.mlog = logging.getLogger('mongo')
        self.lolog = logging.getLogger('lookup')
        self.plog = logging.getLogger('preprocesser')
        self.glog = logging.getLogger('grapher')

    def route_args(self, args):
        if args['--del']:
            ana = Compresser('n', 'tot')
            d = ana.hit_ph()
            dr = ana.sort_date(ana.bind_clusters(d))

            for k, v in dr.iteritems():
                yield k, ' '*(len('Tue May 13 14:46')+5-len(k)), v