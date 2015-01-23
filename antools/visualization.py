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
from sklearn.metrics import confusion_matrix


def plotresults(df, truecol, predcol):
    plt.figure(figsize=[3,2.5])
    if len(df[predcol].unique())<5:
        mat = confusion_matrix(df[truecol], df[predcol])
        labels=['1 star','2 stars','3 stars','4 stars']
        countsdf=pd.DataFrame(data=mat, columns=labels)
        propdf=countsdf.divide(countsdf.sum(axis=1), axis='rows')
        mat=propdf.values
        plotconfmat(mat, labels)
        plt.show()
        return pd.DataFrame(index=labels, columns=labels, data=mat)
    else:
        df.plot(predcol, truecol, kind='scatter')
        plt.show()
        

def plotconfmat(conf, labels):
    conf=conf*100
    heatmap = plt.pcolor(conf, cmap='Blues', vmax=100, vmin=0)
    plt.ylabel('true')
    plt.xlabel('predicted')
    plt.xticks(np.arange(len(labels)),labels)
    plt.yticks(np.arange(len(labels)),labels)
    plt.colorbar()
    
def customlegend(colordict, loc=[1,0], alpha=1):
    recs=[]
    keys=colordict.keys()
    for key in keys:
        recs.append(Rectangle((0,0),1,1,fc=colordict[key]))
    return plt.legend(recs, keys, loc=loc)
    
def alphapallete(palletename, n_colors, alpha):
    return [(tup[0],tup[1],tup[2], alpha) for tup in sns.color_palette(palletename, n_colors=n_colors)]
    
