from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base

import sys, os
rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
sys.path.append(os.path.join(rootdir, 'Projects', 'credentials'))
from sqlcfg import host, user, passwd

projectroot='/Projects/cragcrunch/'

fulldir=os.path.join(rootdir, 'Projects/cragcrunch')

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


# model parameters

from sklearn.ensemble import RandomForestClassifier

class RandomForestClassifierWithCoef(RandomForestClassifier):
    '''extension of the RandomForectClassifier class that allows me to call coef_ instead of feature_importances_ (for ease/consistency with APIs of other models)'''
    def fit(self, *args, **kwargs):
        super(RandomForestClassifierWithCoef, self).fit(*args, **kwargs)
        self.coef_ = self.feature_importances_

clf=RandomForestClassifierWithCoef(n_estimators=40, oob_score=True) #n_estimators selected from CV performance on exploratory (NH) data