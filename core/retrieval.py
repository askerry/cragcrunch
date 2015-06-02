# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:45:53 2015

@author: amyskerry

This module contains functions for interfacing with the database.
"""

def query_filter(dbname, condition_dict, colname):
    "takes name of database and set of simple equality conditions and returns values of single column"
    return colvalues
    
def check_for_existing(climbid, kind):
    if kind=='area':
        return        
    if kind=='region':
        return
        
        
def is_hit(userid, climbid):
    '''returns whether userid has climbed climbid'''
    return boolean
    
def get_pageviews(areaid):
    '''returns number of views of subareas in the area of areaid'''
    return areaids, views

def get_candidates(user, area, **kwargs):
    return candidates
    
def get_users_climbs(userid):
    '''take userid and return dict containing climbs the user has rated, and the scores given'''
    return userclimbs
    
def get_users_who_climbed(climbid):
    '''takes a climbid and returns a dict containing the climbers that have climbed that climb, and the scores they gave it'''
    return climbers
    
def get_popularity(climbid):
    '''returns popularity of climb from database'''
    return score
    
def get_url(id_num, kind='climb'):
    '''takes url and kind variable specifying table, and returns relevant url'''
    return url
    
def save_update_to_db(obj):
    pass