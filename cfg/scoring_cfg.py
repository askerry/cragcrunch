# -*- coding: utf-8 -*-
"""
Created on Wed May 27 15:54:45 2015

@author: amyskerry
"""

class SimilarityCfg():
    def __init__(self, features, weights=None, metric='Cosine'):
        self.metric=metric
        self.features=features
        if weights is None:
            self.weights=[1 for f in features]
            