#!/usr/bin/env python

__author__ = 'chris'
__version__ = 'Version 05.02'

from pymongo import Connection


class Mongo:

    def __init__(self):
        con = Connection()
        db = con.aivb_db
        self.articles = db.articles

    def insert_db(self, obj):
        self.articles.insert(obj)

    def populate_db(self, dict):
        for art in dict:
            self.articles.insert(art)

    # TODO: merge these into one function
    def grab_all(self):
        res = self.articles.find()
        for art in res:
            print art

    def grab_one(self):
        return self.articles.find_one()

    def grab_row(self, key, value):
        print key, value
        res = self.articles.find({key: value})
        for art in res:
            print art

    def grab_regex(self, key, pattern):
        res = self.articles.find({key: {'$regex': pattern}})
        for art in res:
            print art

    def clear_all(self, v=None):
        for art in self.articles.find():
            if v:
                print art
            self.articles.remove(art)
