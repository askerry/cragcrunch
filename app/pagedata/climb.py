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
    cdict=deepcopy(c.__dict__)
    cdict['climbid']=int(cdict['climbid'])
    cdict['areaname']=db.session.query(AreaTable).filter_by(areaid=int(c.area)).first().name
    cdict['mainarea']=db.session.query(AreaTable).filter_by(areaid=int(c.area)).first().mainarea
    try:
        cdict['mainarea_name']=db.session.query(AreaTable).filter_by(areaid=cdict['mainarea']).first().name
        cdict['region']=db.session.query(AreaTable).filter_by(areaid=cdict['mainarea']).first().region
    except:
        cdict['mainarea_name']=''
        cdict['region']=db.session.query(AreaTable).filter_by(areaid=cdict['area']).first().region
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
    projdir=os.path.join(rootdir, 'Projects','cragcrunch','data', 'user_sim_matrix.csv')
    df=pd.read_csv(projdir)
    climbindices=np.argsort(df.loc[climbid,:].values)[-6:-1]
    simids=df.columns.values[climbindices].astype(float)
    ids=db.session.query(ClimbTable).all()
    ids=[float(el.climbid) for el in ids]
    simclimbids=[el for el in simids if el in ids]
    simclimbobjs=[db.session.query(ClimbTable).filter_by(climbid=climbid).first() for climbid in simclimbids]
    simclimbdicts=[getclimbdict(o,db) for o in simclimbobjs]
    return simclimbdicts
