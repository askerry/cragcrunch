# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:46:32 2015

@author: amyskerry

This module contains functions for computing similarity between climbers and climbs.
"""

import numpy as np

def get_climb_similarity(climbid1, climbid2, climbsim_cfg=None):
    '''takes two climbs and returns their similarity in some feature space'''
    similarity = np.random.choice(np.linspace(1, -1))
    confidence = np.random.rand()
    return similarity, confidence
    
def get_climber_similarity(climberid1, climberid2, usersim_cfg=None):
    '''takes two climbers and returns their similarity in some feature space'''
    similarity = np.random.choice(np.linspace(1, -1))
    confidence = np.random.rand()
    return similarity, confidence