# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:17:48 2015

@author: amyskerry
"""

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable, ToDosTable
import numpy as np
import viz
import pandas as pd
import os

from config import rootdir


##################################################
#                Climb Page Functions             #
##################################################

def getareanest(areaid, db,areanest=[], nestednames=[]):
    local=db.session.query(AreaTable).filter_by(country = 'USA').all()
    regions=set([l.region for l in local])
    name=db.session.query(AreaTable).filter_by(areaid=areaid).first().name
    if name not in regions:
        parent=db.session.query(AreaTable).filter_by(areaid=areaid).first().area
        parentname=db.session.query(AreaTable).filter_by(areaid=areaid).first().name
        areanest.append(parent)
        nestednames.append(parentname)
        getareanest(parent, db, areanest, nestednames)
    return areanest, nestednames

def getclimbdict(c, db):
    cdict=c.__dict__
    cdict['climbid']=int(cdict['climbid'])
    cdict['areaname']=db.session.query(AreaTable).filter_by(areaid=int(c.area)).first().name
    cdict['mainarea']=db.session.query(AreaTable).filter_by(areaid=int(c.area)).first().mainarea
    try:
        cdict['mainarea_name']=db.session.query(AreaTable).filter_by(areaid=cdict['mainarea']).first().name
        cdict['region']=db.session.query(AreaTable).filter_by(areaid=cdict['mainarea']).first().region
    except:
        cdict['mainarea_name']=''
        cdict['region']=db.session.query(AreaTable).filter_by(areaid=cdict['area']).first().region
    cdict['length']="%s ft" %cdict['length']
    nestedids,nestednames=getareanest(cdict['area'], db)
    cdict['nest']=' -- '.join(nestednames)
    return cdict
    
def getsimilarclimbs(db, climbid):
    projdir=os.path.join(rootdir, 'Projects','cragcrunch','data', 'user_sim_matrix.csv')
    df=pd.read_csv(projdir)
    print "xxxx"
    print climbid
    climbindices=np.argsort(df.ix[climbid,:].values)[-5:]
    simclimbs=df.columns[climbindices]
    return simclimbs