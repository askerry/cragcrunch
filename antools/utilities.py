# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:11:44 2015

@author: amyskerry
"""

import clean
import miscdf
import randomstuff as rd
import numpy as np
import pickle
import pandas as pd

def cleandf(df):
    '''apply various functions to clean string inputs from html'''
    nanvalues=['','None','unavailable', None]
    df=df.applymap(lambda x:np.nan if x in nanvalues else x)
    for col in df.columns:
        if col in ('climbid', 'areaid', 'climberid', 'ticksid', 'commentsid', 'gradesid', 'starid', 'todosid', 'climb', 'climber', 'area'):
            df[col]=df[col].convert_objects(convert_numeric=True).values
        elif col in ('starsscore', 'age', 'avgstars'):
            df[col]=df[col].convert_objects(convert_numeric=True).values
        elif col =='pageviews':
            df[col]=df[col].apply(clean.removecomma)
        elif col=='maplocation':
            df['latitude']=df[col].apply(clean.getlat)
            df['longitude']=df[col].apply(clean.getlong)
            del df['maplocation']
        elif col in ('elevation', 'length'):
            df[col]=df[col].apply(clean.striplength)
        elif col=='pitch':
            df[col]=df[col].apply(clean.pitch)
        else:
            df[col]=df[col].apply(clean.strip)
        if col=='url':
            df['urlname']=df[col].apply(clean.extractname)
        if col=='style':
            df[col]=df[col].apply(clean.mergeiceandsnow)
        if col =='pitch':
            df[col]=df[col].apply(clean.strippitch)

    return df
    
def dedupsandmissing(full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf):
    '''deal with duplicated/missing areas and climbers'''
    full_areadf=clean.dedupareas(full_areadf) 
    full_climberdf=clean.dedupclimbers(full_climberdf)
    full_tickdf= clean.addmissingclimbers(full_climberdf, full_tickdf)
    full_commentdf = clean.addmissingclimbers(full_climberdf, full_commentdf)
    full_gradedf = clean.addmissingclimbers(full_climberdf, full_gradedf)
    full_tododf= clean.addmissingclimbers(full_climberdf, full_tododf)
    full_stardf = clean.addmissingclimbers(full_climberdf, full_stardf)
    return full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf
    
def reindexall(full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf):
    '''reindex everything so that id is index'''
    full_climbdf.index=full_climbdf.climbid
    full_areadf.index=full_areadf.areaid
    full_climberdf.index=full_climberdf.climberid
    full_tickdf.index=full_tickdf.ticksid
    full_commentdf.index=full_commentdf.commentsid
    full_gradedf.index=full_gradedf.gradesid
    full_stardf.index=full_stardf.starid
    full_tododf.index=full_tododf.todosid
    full_hitsdf.index=full_hitsdf.hitsid
    return full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf

def renameindices(full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf, mainareadf):
    full_climbdf.index.rename('index', inplace=True)
    full_areadf.index.rename('index', inplace=True)
    full_climberdf.index.rename('index', inplace=True)
    full_tickdf.index.rename('index', inplace=True)
    full_commentdf.index.rename('index', inplace=True)
    full_gradedf.index.rename('index', inplace=True)
    full_stardf.index.rename('index', inplace=True)
    full_tododf.index.rename('index', inplace=True)
    full_hitsdf.index.rename('index', inplace=True)
    mainareadf.index.rename('index', inplace=True)
    return full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf,mainareadf
    
def pickletheseobjects(filename, objects):
    '''takes list of objects and pickles them to <filename>'''
    with open(filename, 'wb') as output:
        pickler = pickle.Pickler(output, pickle.HIGHEST_PROTOCOL)
        for obj in objects:
            try:
                pickler.dump(obj)
            except:
                print "pickle fail"
            
def loadpickledobjects(filename):
    '''takes <filename> and loads it, returning list of objects'''
    with open(filename, 'r') as inputfile:
        remaining=1
        objects=[]
        while remaining:
            try:
                objects.append(pickle.load(inputfile))
            except:
                remaining=0
    return objects
 
def isfloatable(x):   
    try:
        float(x)
        return True
    except:
        return False
 
def normalizewordcounts(climbdf, features,key):
    '''replace word counts with word counts normalized by length of text'''
    climbdf=climbdf.copy()
    climbs=climbdf['climbid'].values
    fullcontent=climbdf[key].values #len of description
    X=climbdf.loc[climbs,features].values #training features are word counts
    desclen=np.array([float(len(x)) if isinstance(x,str) else 0 for x in fullcontent]) #get length of each description
    X=(X.T/desclen).T #normalize word counts by length of description
    climbdf.loc[climbs,features]=X
    return climbdf
    
def gettextfeats(cdf, allterms):
    descripfeats=['%s_description' %(h) for h in allterms]
    #normalize all text by length of text
    cdf.index=cdf.climbid.values
    return descripfeats, cdf
    

def makecols(sorteddf):
    feats=[col[:col.index('_')+1] if '_' in col and '_avg' not in col else col for col in sorteddf.index.values]
    feats=list(set(feats))
    feats=[feat for feat in feats if feat !='other_avg']
    feats.append('crimp_') #it's my favorite feature
    finalfeats=[]
    for f in feats:
        if f=='other_avg' or '_' not in f:
            finalfeats.append(f)
        else:
            finalfeats.append(f+'description')
    return finalfeats