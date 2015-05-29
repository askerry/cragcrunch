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


#database parameters
class Cfg():
    def __init__(self):
        self.projectroot = projectroot
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = 'climbdb2'
        self.charset = 'utf8'
        self.use_unicode = 0
        self.clobber = False
    pass
cfg=Cfg()