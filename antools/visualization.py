# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 12:55:31 2015

@author: amyskerry
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.patches import Rectangle

def plotconfmat(conf, labels):
    conf=conf*100
    heatmap = plt.pcolor(conf, cmap='Blues', vmax=100, vmin=0)
    plt.ylabel('true')
    plt.xlabel('predicted')
    plt.xticks(np.arange(len(labels))+.5,labels)
    plt.yticks(np.arange(len(labels))+.5,labels)
    plt.colorbar()
    
def customlegend(colordict, loc=[1,0], alpha=1):
    recs=[]
    keys=colordict.keys()
    for key in keys:
        recs.append(Rectangle((0,0),1,1,fc=colordict[key]))
    return plt.legend(recs, keys, loc=loc)
    
def alphapallete(palletename, n_colors, alpha):
    return [(tup[0],tup[1],tup[2], alpha) for tup in sns.color_palette(palletename, n_colors=n_colors)]
    
