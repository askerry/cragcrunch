# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 12:21:52 2015

@author: amyskerry
"""

import numpy as np
import pandas as pd

from joblib import Parallel, delayed  
import multiprocessing
num_cores = multiprocessing.cpu_count()
print "%s cores available for parallel processing" % num_cores



def modelnewuser(clf, userdf, samplesdf, featdf, newuserfeats):
    '''takes dataframe with user, feature, and preferencescore, creates and stores a reduced model for user recommendations'''
    Y=np.array(rateallclimbs(userdf, samplesdf, featdf, newuserfeats))
    X=samplesdf.values
    clf.fit(X,Y)
    return clf
    
def makefeatdf(cdf, reducedfeats):
    means=cdf[reducedfeats].describe().loc['mean',:]
    medians=cdf[reducedfeats].describe().loc['mean',:]
    stds=cdf[reducedfeats].describe().loc['std',:]
    high=medians+1*stds
    medhigh=medians+.5*stds
    medlow=means
    low=means-.25*stds
    dfdict={'feature':reducedfeats,'high':high.values, 'medhigh':medhigh.values,'medlow':medlow.values, 'low':low.values}
    return pd.DataFrame(data=dfdict)
    
def makesampleclimbs(reducedfeats, featdf):
    mat=[]
    possl=['low','medlow','medhigh','high']
    for i in range(20):
        rowtypes=[np.random.choice(possl) for r in reducedfeats]
        rowvals=[featdf.loc[featdf['feature']==r, rowtypes[rn]].values[0] for rn,r in enumerate(reducedfeats)]
        mat.append(rowvals)
    return pd.DataFrame(data=np.array(mat), columns=reducedfeats)

def getscore(featdf,f,val):
    '''get score that this value is associated with for this feature f'''
    rowvals=list(featdf[featdf['feature']==f][[1,2,3,4]].values[0])
    return rowvals.index(val)+1
    
def rateclimb(userdf, sampledf, featdf, reducedfeats):
    '''compute users rating of the climb given their expressed preferences and the climb's features'''
    ratings=[]
    for f in reducedfeats:
        value=sampledf[f]
        fscore=getscore(featdf,f,value)
        userscore=userdf[userdf['feature']==f]['pref'].values[0]
        ratings.append(4-np.abs(fscore-userscore))
    return np.mean(ratings)

    
def rateallclimbs(userdf, samplesdf, featdf, reducedfeats):
    '''get climber's ratings on all climbs in sample set'''
    ratings=samplesdf.apply(lambda x:rateclimb(userdf, x[:], featdf, reducedfeats), axis=1)
    return ratings       