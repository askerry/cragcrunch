# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:11:44 2015

@author: amyskerry
"""

import numpy as np
import pickle
    
def pickletheseobjects(filename, objects):
    '''takes list of objects and pickles them to <filename>'''
    with open(filename, 'wb') as output:
        pickler = pickle.Pickler(output, pickle.HIGHEST_PROTOCOL)
        for obj in objects:
            try:
                pickler.dump(obj)
            except:
                print "pickle fail"
            
def loadpickledobjects(filename):
    '''takes <filename> and loads it, returning list of objects'''
    with open(filename, 'r') as inputfile:
        remaining=1
        objects=[]
        while remaining:
            try:
                objects.append(pickle.load(inputfile))
            except:
                remaining=0
    return objects
 
