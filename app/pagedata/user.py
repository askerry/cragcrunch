# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:12:37 2015

@author: amyskerry
"""
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
import numpy as np
import viz

from config import rootdir


##################################################
#                User Page Functions             #
##################################################

def getuserdict(u,db):
    udict=u.__dict__
    udict['climberid']=int(udict['climberid'])
    udict['age']="%s years" %udict['age']
    udict['mainarea_name']=db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().name
    udict['region']=db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().region
    udict['country']=db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().country
    return udict
    
def getuserplots(udict,db):
    plotdata=[]
    return plotdata
    
def getuserrecs(udict, db):
    userid=udict['climberid']
    recclimbs=[]
    return recclimbs