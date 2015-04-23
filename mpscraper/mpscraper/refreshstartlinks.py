# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 20:00:14 2015

@author: amyskerry
"""

#general
import pandas as pd
import numpy as np
np.random.RandomState(100)
from sqlalchemy import create_engine
import MySQLdb
import os
import sys
import us
sys.setrecursionlimit(3000)

#project specific code
from cfgdb import cfg

#misc config
rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
rootdir=os.path.join(rootdir, 'Projects','cragcrunch')

con=MySQLdb.connect(user=cfg.user, passwd=cfg.passwd, db=cfg.dbname, host=cfg.host, charset=cfg.charset, use_unicode=cfg.charset)
#stateurls = pd.read_sql("SELECT name, region,url from Area where region in ('World', '* In Progress') and name in %s" %(states), con)
areaurls = pd.read_sql("SELECT name, region,url from Area", con)
userurls = pd.read_sql("SELECT name, url from Climber", con)

with open("areaurls.txt", 'wb') as f:
    urls=areaurls.url.values
    urls=["http://"+url for url in urls]
    f.write(', '.join(urls))
print "refreshed area urls"
print len(urls)

with open("userurls.txt", 'wb') as f:
    urls=userurls.url.values
    urls=["http://"+url for url in urls]
    f.write(', '.join(urls))
print "refreshed user urls"
print len(urls)
