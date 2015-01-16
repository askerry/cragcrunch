# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:18:49 2015

@author: amyskerry
"""

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable, ToDosTable
import numpy as np
import pandas as pd
import viz

from config import rootdir


##################################################
#                Area Page Functions             #
##################################################

def getplotdata(climbids, db):
    output=db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).all()
    cdict=output[0].__dict__
    cols=cdict.keys()
    datadict={}
    for c in cols:
        datadict[c]=[row.__dict__[c] for row in output]
    plotdf=pd.DataFrame(data=datadict)
    plotdf.index=plotdf.climbid.values
    viz.visualizearea(plotdf)
    

def getareadict(a,db):
    adict=a.__dict__
    adict['areaid']=int(adict['areaid'])
    popclimbs, allchildren=getpopclimbs(db, adict['areaid'])
    adict['popclimbs']={p['climbid']:p['name'] for p in popclimbs}
    adict['similarareas']=getsimilarareas(db,adict['areaid'])
    adict['allchildren']=allchildren
    return adict

def getsubareas(db, areaid):
    subareaids=db.session.query(AreaTable).filter_by(area=areaid).all()
    subareaids=[sub.areaid for sub in subareaids]
    for areaid in subareaids:
        subareaids.extend(getsubareas(db, areaid))
    return subareaids

def getchildren(db, areaid):
    areaids=getsubareas(db, areaid)
    childrenids=db.session.query(ClimbTable).filter(ClimbTable.area.in_(areaids)).all()
    childrenids=[c.climbid for c in childrenids]
    return childrenids

def getpopclimbs(db, areaid):
    climbids=getchildren(db, areaid)
    c=db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).order_by('pageviews').all()[-5:]
    popclimbs = [climb.__dict__ for climb in c]
    return popclimbs, climbids

def getsimilarareas(db, areaid):
    print "not implemented yet"
    return []