# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:17:48 2015

@author: amyskerry
"""

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
import numpy as np
import viz
import pandas as pd
import os
from copy import deepcopy
import timeit
from config import rootdir


##################################################
#                Climb Page Functions             #
##################################################

def getareanest(areaid, db,areanest=None, nestednames=None):
    if areanest is None:
        areanest=[]
    if nestednames is None:
        nestednames=[]
    local=db.session.query(AreaTable).filter_by(country = 'USA').all()
    regions=list(set([l.region for l in local]))
    name=db.session.query(AreaTable).filter_by(areaid=areaid).first().name
    if name not in regions and len(areanest)<8:
        parent=db.session.query(AreaTable).filter_by(areaid=areaid).first().area
        parentname=db.session.query(AreaTable).filter_by(areaid=parent).first().name
        areanest.append(parent)
        nestednames.append(parentname)
        getareanest(parent, db, areanest, nestednames)
    elif name not in regions:
        regionname=db.session.query(AreaTable).filter_by(areaid=areaid).first().region
        regionid=db.session.query(AreaTable).filter_by(name=regionname, region='World').first().areaid
        areanest.append(regionid)
        nestednames.append(regionname)
    return areanest, nestednames


def getclimbdict(c, db, getnest=False):
    #t=timeit.default_timer()
    #cdict=deepcopy(c.__dict__)
    cdict=c.__dict__
    #print "copy: %.6f" %(timeit.default_timer()-t)
    cdict['climbid']=int(cdict['climbid'])
    if cdict['length']>0:
        cdict['length']="%s ft" %int(cdict['length'])
    else:
        cdict['length']=""
    if cdict['pitch']==1:
        cdict['pitch']="%s pitch" %int(cdict['pitch'])
    elif cdict['pitch']>1:
        cdict['pitch']="%s pitches" %int(cdict['pitch'])
    else:
        cdict['length']=""
    cdict['pageviews']=int(cdict['pageviews'])
    if cdict['avgstars']==1:
        cdict['avgstars']="%.1f star" %(cdict['avgstars'])
    elif cdict['avgstars']>1:
        cdict['avgstars']="%.1f stars" %(cdict['avgstars'])
    else:
        cdict['avgstars']="no stars"
    cdict['description']=cdict['description'].replace('. \n','<br><br>')
    if getnest:
        nestedids,nestednames=getareanest(cdict['area'], db)
        cdict['nest']=zip(nestedids, nestednames)
    return cdict
    
def getsimilarclimbs(db, climbid, ClimbTable):
    '''get climbs similar to target'''
    df=pd.read_sql('select * from simclimbs', db.engine, index_col='climbid')
    simclimbids=df.loc[climbid,:].values[1:6].astype(int)
    simclimbobjs=[db.session.query(ClimbTable).filter_by(climbid=c).first() for c in simclimbids]
    simclimbdicts=[getclimbdict(o,db) for o in simclimbobjs]
    return simclimbdicts
