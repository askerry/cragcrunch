# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:20:26 2015

@author: amyskerry
"""
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable, ToDosTable
import numpy as np
import viz

from config import rootdir


##################################################
#                Home Page Functions             #
##################################################
    
def gettopclimbs(g):
    #topclimbs = g.db.rawsql('select climbid, name from climb_prepped where pageviews> 30000 limit 10;')
    topclimbs=g.db.session.query(ClimbTable).filter(ClimbTable.pageviews>50000).all()[:10]
    tdict={c.name:c.climbid for c in topclimbs}
    return tdict

def findmatch(text,g):
    matchids={'climbs':[],'areas':[], 'users':[]}
    matchstr='%'+text+'%'
    climbmatches=g.db.session.query(ClimbTable).filter(ClimbTable.name.ilike(matchstr)).all()
    for c in climbmatches:
        cd={'climbid':c.climbid, 'name':c.name, 'region':c.region}
        matchids['climbs'].append(cd)
    areamatches=g.db.session.query(AreaTable).filter(AreaTable.name.ilike(matchstr)).all()
    for a in areamatches:
        ad={'areaid':a.areaid, 'name':a.name, 'region':a.region}
        matchids['areas'].append(ad)
    usermatches=g.db.session.query(ClimberTable).filter(ClimberTable.name.ilike(matchstr)).all()
    for u in usermatches:
        ud={'climberid':int(u.climberid), 'name':u.name, 'location':u.mainarea}
        matchids['users'].append(ud)
    return matchids
    
