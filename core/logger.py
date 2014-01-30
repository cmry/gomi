#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'chris'

import logging
import os

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

        self.rlog = logging.getLogger('scraper')
        self.nlog = logging.getLogger('nu.nl')
        self.tlog = logging.getLogger('tweakers')
        self.elog = logging.getLogger('eval')
        self.halt = False
