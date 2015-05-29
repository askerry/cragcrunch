# -*- coding: utf-8 -*-
"""
Created on Mon Feb  2 22:11:02 2015

@author: amyskerry
"""

import os
import sys
from sqlalchemy import create_engine
import pandas as pd
sys.path.append('mpscraper')
from mpscraper.cfgdb import cfg
sys.path.append('antools')
import antools.randomstuff as rd
import antools.reduction as red
import antools.utilities as util
import antools.visualization as viz
import antools.modeling as mo
import antools.newusermodeling as nmo

rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
projdir=os.path.join(rootdir, 'Projects','cragcrunch','data')

engine = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' %(cfg.user, cfg.host, cfg.dbname, cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)


featsdict=util.loadpickledobjects(os.path.join(projdir,'learnedfeatures.pkl'))[0]
allfeats=featsdict['alltextfeats']
reducedfeats=featsdict['reducedtextfeats']

like_mat= pd.read_sql("SELECT * from like_matrix", engine, index_col='index')


allfeats=['avgstars']+reducedfeats+list(like_mat.columns)
redfeats=['avgstars']+reducedfeats

#allfeats
modeldir=os.path.join(projdir,'models')
modelfiles=os.listdir(modeldir)
for f in modelfiles:
    if f[:5]=='user_':
        filename=os.path.join(modeldir, f)
        traineddict=util.loadpickledobjects(filename)[0]
        traineddict['finalfeats']=allfeats
        traineddict['redfeats']=redfeats
        util.pickletheseobjects(filename, [traineddict])