# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:58:20 2015

@author: amyskerry
"""

import sys, os
rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
sys.path.append(os.path.join(rootdir, 'Projects', 'credentials'))
from sqlcfg import projectroot, host, user, passwd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


#database parameters
class Cfg():
    def __init__(self):
        self.projectroot = projectroot
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = 'climbdb'
        self.charset = 'utf8'
        self.use_unicode = 0
        self.clobber = False
    pass
cfg=Cfg()

class DBConnection():
    def __init__(self, engine):
        Session = sessionmaker(bind=engine)  # create a configured "Session" class
        self.session = Session()  # create a Session
        self.engine = engine

    def close(self):
        self.session.close()

    def rawsql(self, string):
        '''to fall back on raw sql queries when necessary'''
        sql = text(string)
        returned = self.engine.execute(sql)
        entries = []
        for row in returned:
            entries.append(dict(title=row[0], text=row[1]))
        return entries


def connect_db(app):
    #create engine that Session will use for connection
    cfg = app.config['DBCFG']
    engine = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' % (
    cfg.user, cfg.host, cfg.dbname, cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)
    return DBConnection(engine)