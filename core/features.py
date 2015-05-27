# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:47:05 2015

@author: amyskerry

This module contains functions for accessing and processing features of climbs.
"""

def get_climb_attribute_scores(climbid, climbattributes):
    '''take climb and return scores on each of the prespecified attributes'''
    for attr in climbattributes:
        attribute_dict[attr]=get_climb_score(climbid, attr)
    return attribute_dict
    
def get_climb_score(climbid, attr):
    '''return score of climb on the specified dimension'''
    return score