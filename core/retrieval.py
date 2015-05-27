# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:45:53 2015

@author: amyskerry

This module contains functions for interfacing with the database.
"""

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