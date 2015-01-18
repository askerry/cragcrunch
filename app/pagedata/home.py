# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:20:26 2015

@author: amyskerry
"""
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
import numpy as np
import viz

from config import rootdir


##################################################
#                Home Page Functions             #
##################################################
    
def gettopclimbs(g):
    #topclimbs = g.db.rawsql('select climbid, name from climb_prepped where pageviews> 30000 limit 10;')
    topclimbs=g.db.session.query(ClimbTable).filter(ClimbTable.pageviews>50000).all()[:10]
    tlist=[{'name':c.name,'climbid':c.climbid, 'pageviews':int(c.pageviews), 'mainarea_name':g.db.session.query(AreaTable).filter_by(areaid=c.mainarea).first().name, 'region':c.region} for c in topclimbs]
    return tlist

def findmatch(text,g):
    text=text.strip()
    if text !='':
        matchids={'climbs':[],'areas':[], 'users':[]}
        matchstr='%'+text+'%'
        climbmatches=g.db.session.query(ClimbTable).filter(ClimbTable.name.ilike(matchstr)).all()
        for c in climbmatches:
            mainarea_name=g.db.session.query(AreaTable).filter_by(areaid=c.mainarea).first().name
            cd={'climbid':c.climbid, 'name':c.name, 'mainarea_name':mainarea_name, 'region':c.region, 'grade':c.grade, 'style':c.style, 'url':c.url}
            matchids['climbs'].append(cd)
        areamatches=g.db.session.query(AreaTable).filter(AreaTable.name.ilike(matchstr)).all()
        for a in areamatches:
            mainarea_name=g.db.session.query(AreaTable).filter_by(areaid=a.mainarea).first().name
            ad={'areaid':a.areaid, 'name':a.name, 'mainarea_name':mainarea_name, 'region':a.region, 'url':c.url}
            matchids['areas'].append(ad)
        usermatches=g.db.session.query(ClimberTable).filter(ClimberTable.name.ilike(matchstr)).all()
        for u in usermatches:
            mainarea_name=g.db.session.query(AreaTable).filter_by(areaid=u.mainarea).first().name
            ud={'climberid':int(u.climberid), 'name':u.name, 'mainarea_name':mainarea_name, 'region':u.region, 'url':c.url}
            matchids['users'].append(ud)
        return matchids
    else:
        return {'users':[{}],'areas':[{}],'climbds':[{}]}
    
