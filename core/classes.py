# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:42:35 2015

@author: amyskerry

This module contains definition of main classes.
"""

class User():
    def __init__(self, climberid):
        self.id=climberid
        self.attributes={} #boulder, trd, soport, grades
    def load_preferences(self):
        self.preferences={} #this dict will contain preference attributes and signed strengths (.9= really like, -.9= really hate, -.1=indifferent)
