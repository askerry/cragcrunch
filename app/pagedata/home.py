# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:20:26 2015

@author: amyskerry
"""
from flask import current_app
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
from sqlalchemy import between
import numpy as np
import warnings
from collections import OrderedDict
from config import rootdir


# #################################################
#                Home Page Functions             #
##################################################

def gettopclimbs(db):
    '''get top climbs by pageviews for naive viewers'''
    topclimbs = db.session.query(ClimbTable).order_by(ClimbTable.pageviews.desc()).limit(10).all()
    tlist = [{'name': c.name, 'url': c.url, 'mainarea': int(c.mainarea), 'climbid': c.climbid, 'pageviews': int(c.pageviews),
              'mainarea_name': db.session.query(AreaTable).filter_by(areaid=c.mainarea).first().name,
              'region': c.region} for c in topclimbs]
    return tlist


def getusers(db):
    '''get list of all possible users in the databse'''
    userkeys=[c for c in current_app.modeldicts.keys() if 'user' in c]
    climberids = [c[5:] for c in userkeys]
    climberids = [float(c[:c.index('_')]) for c in climberids]
    climbers = db.session.query(ClimberTable).filter(ClimberTable.climberid.in_(climberids)).all()
    names = [climber.name for climber in climbers]
    ids = [climber.climberid for climber in climbers]
    sortedindices = np.argsort(names)
    return OrderedDict((ids[i], names[i]) for i in sortedindices)


def getall(g):
    '''get all areas, climbs, climbers'''
    areas = g.db.session.query(AreaTable).all()
    climbs = g.db.session.query(ClimbTable).all()
    climbers = g.db.session.query(ClimberTable).all()
    return [''] + [climber.name for climber in climbers] + [climb.name for climb in climbs] + [area.name for area in
                                                                                               areas]


def findmatch(text, g):
    '''take search text and return info on areas, climbs, and users'''
    text = text.strip()
    if len(text)>2:
        matchids = {'climbs': [], 'areas': [], 'users': []}
        matchstr = '%' + text + '%'
        climbmatches = g.db.session.query(ClimbTable).filter(ClimbTable.name.ilike(matchstr)).all()
        for c in climbmatches:
            mainarea_name = g.db.session.query(AreaTable).filter_by(areaid=c.mainarea).first().name
            cd = {'climbid': c.climbid, 'name': c.name, 'mainarea_name': mainarea_name, 'mainarea': int(float(c.mainarea)), 'region': c.region,
                  'grade': c.grade, 'style': c.style, 'url': c.url}
            matchids['climbs'].append(cd)
        areamatches = g.db.session.query(AreaTable).filter(AreaTable.name.ilike(matchstr)).all()
        for a in areamatches:
            mainarea_name = g.db.session.query(AreaTable).filter_by(areaid=a.mainarea).first().name
            ad = {'areaid': a.areaid, 'name': a.name, 'mainarea_name': mainarea_name, 'mainarea': int(float(a.mainarea)), 'region': a.region, 'url': a.url}
            matchids['areas'].append(ad)
        usermatches = g.db.session.query(ClimberTable).filter(ClimberTable.name.ilike(matchstr)).all()
        for u in usermatches:
            try:
                mainarea_name = g.db.session.query(AreaTable).filter_by(areaid=u.mainarea).first().name
            except:
                warnings.warn("main area not found")
                mainarea_name = 'Unknown Area'
            ud = {'climberid': int(u.climberid), 'name': u.name, 'mainarea_name': mainarea_name, 'mainarea': int(float(u.mainarea)), 'region': u.region,
                  'url': u.url}
            matchids['users'].append(ud)
        return matchids
    else:
        return {'users': [{}], 'areas': [{}], 'climbs': [{}]}
    
