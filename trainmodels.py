# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 21:25:49 2015

@author: amyskerry
"""

import pandas as pd
import numpy as np
np.random.RandomState(100)
from sqlalchemy import create_engine
import os
import sys
import scipy.stats

sys.path.append('mpscraper')
from mpscraper.cfgdb import cfg
sys.path.append('antools')
import antools.randomstuff as rd
import antools.reduction as red
import antools.utilities as util
import antools.visualization as viz
import antools.modeling as mo
import antools.newusermodeling as nmo


import pandas as pd
import numpy as np
import seaborn as sns
sns.set_style('white')
import matplotlib.pyplot as plt
import scipy.stats

from sklearn.metrics.pairwise import pairwise_distances
import sklearn.cross_validation
from sklearn.ensemble import RandomForestRegressor 
from sklearn.ensemble import RandomForestClassifier 
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.linear_model import Ridge
from sklearn.metrics import f1_score

import sys, os
rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
projdir=os.path.join(rootdir, 'Projects','cragcrunch','data')


engine = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' %(cfg.user, cfg.host, cfg.dbname, cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)
cdf = pd.read_sql("SELECT * from climb_prepped where region='California'", engine, index_col='index')
adf = pd.read_sql("SELECT * from area_prepped where region='California'", engine, index_col='index')
climbs=list(cdf.climbid.unique())
print "loading %s climbs" %(len(climbs))
cldf = pd.read_sql("SELECT * from climber_prepped", engine, index_col='index')
hdf= pd.read_sql("SELECT * from hits_prepped", engine, index_col='index')
sdf= pd.read_sql("SELECT * from stars_prepped", engine, index_col='index')
gdf= pd.read_sql("SELECT * from grades_prepped", engine, index_col='index')
codf= pd.read_sql("SELECT * from comments_prepped", engine, index_col='index')
tdf= pd.read_sql("SELECT * from ticks_prepped", engine, index_col='index')

like_mat= pd.read_sql("SELECT * from like_matrix", engine, index_col='index')
star_mat= pd.read_sql("SELECT * from star_matrix", engine, index_col='index')

minratings=2
users=sdf[sdf['climb'].isin(climbs)]['climber'].unique().astype(int)
users=[u for u in users if u in cldf.climberid.values]
print "starting with %s users" %len(users)
users=[u for u in users if len(sdf[sdf['climber']==u]['climb'].values)>=minratings]
usesdf=sdf[sdf['climber'].isin(users)]
usesdf['other_rounded']=[np.round(val) for val in usesdf['other_avg']]
usesdf=usesdf[(usesdf['starsscore']>0) & (usesdf['other_rounded']>0)]
usesdf['climbid']=usesdf['climb']
ndf=cdf[cdf['climbid'].isin(usesdf['climb'].unique())]
print "reducing to %s users who have greater than or equal to %s ratings provided" %(len(users), minratings)
minratings=5

featsdict=util.loadpickledobjects(os.path.join(projdir,'learnedfeatures.pkl'))[0]
allfeats=featsdict['alltextfeats']
reducedfeats=featsdict['reducedtextfeats']
nestimators=80

compare={'name':[],'acc':[],'recall':[],'precision':[],'f1':[]}
resultsdict={}

name='combined_reduced'
clf=mo.classifier('rfc')
clf.n_estimators=nestimators
numericfeats=['pitch','pageviews','numerizedgrade']
cfeatures=list(like_mat.columns)+reducedfeats
cfeatures.remove('climbid')
sfeatures=['other_avg']
print "classifying using %s features" %(len(cfeatures)+len(sfeatures))
full_ndf=ndf[['climbid']+reducedfeats]
full_ndf=pd.merge(full_ndf, like_mat, on='climbid', how='inner')
full_ndf.index=full_ndf['climbid'].values
full_ndf=full_ndf[full_ndf['climbid'].isin(sdf.climb.unique())]
full_ndf=full_ndf.dropna()
summarydf, resultsdf, informativefeats=mo.classify(clf,users, sfeatures, cfeatures, full_ndf, usesdf, minratings=10, dropself=True, datadir=projdir, getfeats=True)
resultsdict[name]=[summarydf, resultsdf]