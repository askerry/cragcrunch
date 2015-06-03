# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:09:37 2015

@author: amyskerry

This module contains functions for scoring climbs for a single user.
"""

import numpy as np
import db_calls
import json
import sys
sys.path.append('../app')
from ormcfg import ProfileTable


#this might go elsewhere
#from ..cfg import similarity_cfg
#from settings import userfeatures, climbfeatures, climbattributes
#usersim_cfg=similarity_cfg(userfeatures)
#climbsim_cfg=similarity_cfg(climbfeatures)

global defaultscore
defaultscore=2

def finalscore(db, user, climbid, candidates, climbattributes, userclimbs, prefs, allstars, weights=(1,1,1,1)):
    '''return final score for the climb, based on weighted average of the 4 component scores'''
    print "scoring %s" %climbid
    import time
    start=time.time()
    try:
        pop=get_popularity(climbid, candidates)
        users=get_users_who_climbed(climbid, allstars)
        usim=get_usersim_weighted_score(db, users, climbid)
        csim=get_climbsim_weighted_score(db, userclimbs, user['climberid']) #.001
        print time.time()-start
        pscore=get_preference_weighted_score(user, climbid, prefs, climbattributes, candidates) #.0013
        print time.time()-start
        score=np.average([pop, usim, csim, pscore], weights=weights)
        print "score: %s" %score
        return score
    except:
        return defaultscore
    
def get_usersim_weighted_score(db, climbers, userid):
    '''take average of scores of other climber who have climbed the target, weighted by similarity of the climber to the user'''
    try:
        scores,weights=[],[]
        for climberid, userscore in climbers.items():
            scores.append(userscore)
            similarity, confidence = get_climber_similarity(db, userid, climberid)
            weights.append((1 + confidence * similarity)**2)
        return np.average(scores, weights=weights)
    except:
        return defaultscore
    
def get_climbsim_weighted_score(db, userclimbs, climbid):
    '''take average of scores of climbs user has climbed, weighted by similarity of climb to target climb'''
    try:
        scores,weights=[],[]
        for ownclimb, ownscore in userclimbs.items():
            scores.append(ownscore)
            similarity, confidence = get_climb_similarity(db, climbid, ownclimb)
            weights.append((1 + confidence * similarity)**2)
        return np.average(scores, weights=weights)
    except:
        return defaultscore
    
def get_preference_weighted_score(user, climbid, prefs, climbattributes, candidates):
    '''take user and climb and return score weighted by user preferences on prespecified attributes'''
    try:
        attribute_dict=get_climb_attribute_scores(climbid, climbattributes, candidates)
        scores, weights=[],[]
        for attr,score in attribute_dict.items():
            if prefs[attr]<0:
                score=5-score
            weights.append(np.abs(prefs[attr]))
            scores.append(score)
        return np.average(scores, weights=weights)
    except:
        return defaultscore
           
def get_climb_attribute_scores(climbid, climbattributes, candidates):
    '''take climb and return scores on each of the prespecified attributes'''
    attribute_dict={}
    for attr in climbattributes:
        attribute_dict[attr]=candidates[climbid]['t_'+attr]
    return attribute_dict 

def get_popularity(climbid, candidates):
    '''returns popularity of climb from database'''
    return candidates[climbid]['avgstars']
    
def get_climb_similarity(db, climbid1, climbid2, climbsim_cfg=None):
    '''takes two climbs and returns their similarity in some feature space'''
    similarity = np.random.choice(np.linspace(1, -1))
    confidence = np.random.rand()
    return similarity, confidence
    
def get_climber_similarity(db, climberid1, climberid2, usersim_cfg=None):
    '''takes two climbers and returns their similarity in some feature space'''
    similarity = np.random.choice(np.linspace(1, -1))
    confidence = np.random.rand()
    return similarity, confidence
    
def get_users_who_climbed(climbid, allstars):
    '''takes a climbid and returns a dict containing the climbers that have climbed that climb, and the scores they gave it'''
    return {c['climberid']:c['starsscore'] for c in allstars[climbid]}