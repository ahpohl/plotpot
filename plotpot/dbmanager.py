# -*- coding: utf-8 -*-
import sqlite3

class DbManager(object):
    """class for managing the sqlite databases"""
    
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def query(self, arg, bind=()):
        self.cur.execute(arg, bind)
        self.conn.commit()
        return self.cur
    
    def fetchall(self):
        data = self.cur.fetchall()
        return data
    
    def fetchone(self):
        data = self.cur.fetchone()
        return data

    #def __del__(self):
    #    self.conn.close()