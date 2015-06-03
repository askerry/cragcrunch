# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:17:48 2015

@author: amyskerry
"""

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
import numpy as np
import pandas as pd
import os
from sqlalchemy import and_
from copy import deepcopy
import warnings
import timeit
from config import rootdir
import sys
sys.path.append(os.path.join(rootdir, 'cragcrunch/rec/'))
import rec.scoring as scoring


# #################################################
#                Climb Page Functions             #
##################################################

def getareanest(areaid, db, areanest=None, nestednames=None):
    if areanest is None:
        areanest = []
    if nestednames is None:
        nestednames = []
    local = db.session.query(AreaTable).filter_by(country='USA').all()
    regions = list(set([l.region for l in local]))
    name = db.session.query(AreaTable).filter_by(areaid=areaid).first().name
    if name not in regions and len(areanest) < 8:
        parent = db.session.query(AreaTable).filter_by(areaid=areaid).first().area
        parentname = db.session.query(AreaTable).filter_by(areaid=parent).first().name
        areanest.append(int(parent))
        nestednames.append(parentname)
        getareanest(parent, db, areanest, nestednames)
    elif name not in regions:
        regionname = db.session.query(AreaTable).filter_by(areaid=areaid).first().region
        regionid = db.session.query(AreaTable).filter_by(name=regionname, region='World').first().areaid
        areanest.append(int(regionid))
        nestednames.append(regionname)
    return areanest, nestednames


def getclimbdict(c, db, getnest=False):
    cdict = c.__dict__
    try:
        cdict['climbid'] = int(cdict['climbid'])
        cdict['area'] = int(cdict['area'])
        if cdict['length'] > 0:
            try:
                cdict['length'] = "%s ft" % int(cdict['length'])
            except:
                cdict['length'] = ''
        else:
            cdict['length'] = ""
        if cdict['pitch'] == 1:cdict['pitch'] = "%s pitch" % int(cdict['pitch'])
        elif cdict['pitch'] > 1:
            try:
                cdict['pitch'] = "%s pitches" % int(cdict['pitch'])
            except:
                cdict['pitch'] = ""

        else: cdict['pitch'] = ""
        try:
            cdict['pageviews'] = int(float(cdict['pageviews']))
        except:
            cdict['pageviews'] = 0
        if cdict['avgstars'] == 1: cdict['avgstars_string'] = "%.1f star" % cdict['avgstars']
        elif cdict['avgstars'] > 1: cdict['avgstars_string'] = "%.1f stars" % cdict['avgstars']
        else: cdict['avgstars_string'] = "no stars"
        lengear = len(cdict['protection'])
        cdict['description'] = cdict['description'].replace('. \n', '<br><br>')[:-(lengear)]
        if getnest:
            nestedids, nestednames = getareanest(cdict['area'], db)
            cdict['nest'] = zip(nestedids, nestednames)
    except:
        warnings.warn("dictifying failed")
    return cdict


def getsimilarclimbs(db, climbid, cdict, ClimbTable):
    '''get climbs similar to target'''
    grade=cdict['numerizedgrade']
    style=cdict['style']
    if style == 'Boulder': slush=2 
    else: slush=5
    candidates = [c.climbid for c in db.session.query(ClimbTable).filter(and_((ClimbTable.mainarea == cdict['mainarea']),
                                                                               ClimbTable.numerizedgrade.between(
                                                                                   grade-slush,grade+slush),
                                                                               (ClimbTable.style == style))).all()]
    similarities=[scoring.get_climb_similarity(db, climbid, candidate)[0] for candidate in candidates[:100]]
    rank=list(np.argsort(similarities))
    rank.reverse()
    simclimbids = [candidates[i] for i in rank[:5]] 
    simclimbobjs = [db.session.query(ClimbTable).filter_by(climbid=c).first() for c in simclimbids]
    simclimbdicts = [getclimbdict(o, db) for o in simclimbobjs]
    return simclimbdicts


def checkstars(db, climbid, userid):
    try:
        matches = db.session.query(StarsTable).filter(
            and_((StarsTable.climber == userid), StarsTable.climb == climbid)).first()
        return int(matches.starsscore)
    except:
        return 0