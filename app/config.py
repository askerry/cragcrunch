from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base

import sys, os
rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
sys.path.append(os.path.join(rootdir, 'Projects', 'credentials'))
from sqlcfg import projectroot, host, user, passwd


#database parameters

class Cfg():
    def __init__(self, projectroot, host, user, passwd, dbname, charset='utf8', use_unicode=0, clobber=False):
        self.projectroot = projectroot
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.charset = charset
        self.use_unicode = use_unicode
        self.clobber = clobber
DBCFG=Cfg(projectroot, host, user, passwd, dbname='climbdb')
