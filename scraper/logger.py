#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'chris'

import logging

class Logger:

    def __init__(self):
        """ Logger class to display and record operations and errors. """

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='../log/'+str(hash(self))+'.log',
                            filemode='w')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        self.rlog = logging.getLogger('scraper')
        self.nlog = logging.getLogger('nu.nl')
        self.tlog = logging.getLogger('tweakers')
        self.halt = False

        #logger.debug('debug message')
        #logger.info('info message')
        #logger.warn('warn message')
        #logger.error('error message')
        #logger.critical('critical message')
