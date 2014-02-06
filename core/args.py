#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 05.02'


class Arguments(dict):

    def store(self, args):
        self.update(args)