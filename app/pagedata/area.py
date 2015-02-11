# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:18:49 2015

@author: amyskerry
"""

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
import numpy as np
import pandas as pd

from config import rootdir


# #################################################
#                Area Page Functions             #
##################################################


def getareadict(a, db):
    adict = a.__dict__
    adict['areaid'] = int(adict['areaid'])
    localchildren=db.session.query(AreaTable).filter_by(area=adict['areaid']).all()
    adict['subareas']={int(child.areaid):str(child.name) for child in localchildren}
    localchildren_climbs=db.session.query(ClimbTable).filter_by(area=adict['areaid']).all()
    adict['subclimbs']={int(child.climbid):str(child.name) for child in localchildren_climbs}
    adict['pageviews'] = int(adict['pageviews'])
    try:
        adict['climbcount'] = "%s climbs, " % int(adict['climbcount'])
    except:
        adict['climbcount'] = ''
    return adict


def getsubareas(db, areaid):
    subareaids = db.session.query(AreaTable).filter_by(area=areaid).all()
    subareaids = [sub.areaid for sub in subareaids]
    for areaid in subareaids:
        subareaids.extend(getsubareas(db, areaid))
    return subareaids


def getchildren(db, areaid):
    areaids = getsubareas(db, areaid)
    childrenids = db.session.query(ClimbTable).filter(ClimbTable.area.in_(areaids)).all()
    childrenids = [c.climbid for c in childrenids]
    return childrenids


def getpopclimbs(db, areaid):
    climbids = getchildren(db, areaid)
    c = db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).order_by('pageviews').all()[-5:]
    popclimbs = [climb.__dict__ for climb in c]
    return popclimbs, climbids


def getsimilarareas(db, areaid):
    print "not implemented yet"
    return []