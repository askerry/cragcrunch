# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:45:53 2015

@author: amyskerry

This module contains functions for interfacing with the database.
"""
import sys
import numpy as np
import pandas as pd
sys.path.append('../')
from utilities import randomdata as rd
from cfg.database_cfg import cfg, DBConnection
from app.ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable, ProfileTable, HitsTable
from sqlalchemy import create_engine
con = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' % (cfg.user, cfg.host, cfg.dbname+'_prepped', cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)
db=DBConnection(con.engine)

def query_filter(table, condition_dict, colname):
    "takes name of database and set of simple equality conditions and returns values of single column"
    return colvalues
    
def check_for_existing(climbid, kind):
    if kind=='area':
        return        
    if kind=='region':
        return
        
def get_area(areaid):
    '''returns area of areaid'''
    return db.session.query(AreaTable).filter_by(areaid=areaid).first().area

def get_area_name(areaid):
    return db.session.query(AreaTable).filter_by(areaid=areaid).first().name

def get_state_ids():
    states=rd.states.values()
    return [s.areaid for s in db.session.query(AreaTable).filter(AreaTable.name.in_(states)).all()]
        
def is_hit(userid, climbid):
    '''returns whether userid has climbed climbid'''
    return boolean
    
def get_pageviews(areaid):
    '''returns number of views of subareas in the area of areaid'''
    return areaids, views

def get_candidates(user, area, **kwargs):
    return candidates
    
def get_url(id_num, kind='climb'):
    '''takes url and kind variable specifying table, and returns relevant url'''
    return url
    
def find_area(areaname, region, seconddown):
    areas=db.session.query(AreaTable).filter_by(name='Leda').all()
    if len(areas)==0:
        return 2
    if len(areas)==1:
        return areas[0].areaid
    if len(areas)>1:
        areas=[a for a in areas if a.region=='Tennessee']
        try:
            return areas[0].areaid
        except:
            return 2
    
def get_id(url, kind='climb'):
    '''takes a url and returns matching id from the relevant table'''
    if 'http://' in url:
        url=url[7:]
    if 'www.' in url:
        url=url[4:]
    try:
        if kind=='climb':
            return float(db.session.query(ClimbTable).filter_by(url=url).first().climbid)
        elif kind=='area':
            return float(db.session.query(AreaTable).filter_by(url=url).first().areaid)
        elif kind=='climber':
            return float(db.session.query(ClimberTable).filter_by(url=url).first().climberid)
    except:
        return 'new'
        
def save_update_to_db(obj, kind='climb'):
    if kind=='climb':
        if obj.climbid=='new':
            print "creating new climb entry"
        else:
            print "updating climb"
    print obj
    
def update_hits(climberid,climbid):
    pass
