# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:09:37 2015

@author: amyskerry

This module contains functions for scoring climbs for a single user.
"""

import numpy as np
import retrieval
import similarity as sim
import features

#this might go elsewhere
#from ..cfg import similarity_cfg
#from settings import userfeatures, climbfeatures, climbattributes
#usersim_cfg=similarity_cfg(userfeatures)
#climbsim_cfg=similarity_cfg(climbfeatures)


def finalscore(db, user, climbid, weights=(1,1,1,1)):
    '''return final score for the climb, based on weighted average of the 4 component scores'''
    pop=retrieval.get_popularity(climbid)
    usim=get_usersim_weighted_score(user, climbid)
    csim=get_climbsim_weighted_score(user, climbid)
    pscore=get_preference_weighted_score(user, climbid)
    return np.average([pop, usim, csim, pscore], weights)

    
def get_usersim_weighted_score(user, climbid):
    '''take average of scores of other climber who have climbed the target, weighted by similarity of the climber to the user'''
    climbers=retrieval.get_users_who_climbed(climbid)
    scores,weights=[],[]
    for climberid, userscore in climbers.items():
        scores.append(userscore)
        similarity, confidence = sim.get_climber_similarity(user['climberid'], climberid, usersim_cfg)
        weights.append((1 + confidence * similarity)**2)
    return np.average(scores, weights)
    
def get_climbsim_weighted_score(user, climbid):
    '''take average of scores of climbs user has climbed, weighted by similarity of climb to target climb'''
    userclimbs=retrieval.get_users_climbs(user['climberid'])
    scores,weights=[],[]
    for ownclimb, ownscore in userclimbs.items():
        scores.append(ownscore)
        similarity, confidence = sim.get_climb_similarity(climbid, ownclimb, climbsim_cfg)
        weights.append((1 + confidence * similarity)**2)
    return np.average(scores, weights)
    
def get_preference_weighted_score(user, climbid):
    '''take user and climb and return score weighted by user preferences on prespecified attributes'''
    attribute_dict=features.get_climb_attribute_scores(climbid, climbattributes)
    scores, weights=[],[]
    for attr,score in attribute_dict.items():
        if user.preferences[attr]<0:
            score=5-score
        weights.append(np.abs(user.preferences[attr]))
        scores.append(score)
    return np.average(scores, weights)
    