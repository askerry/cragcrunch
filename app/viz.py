# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 16:56:56 2015

@author: amyskerry
"""

import matplotlib.pyplot as plt
import plotly.plotly as plotly
import numpy as np

def save2plotly(f, fname, plotlyprivate=False):
    plotly.sign_in('askerry', 'tn0zp19ph1')
    plotly.plot_mpl(f, filename=fname, auto_open=False, world_readable=plotlyprivate)
    
def visualizearea(df):
    #print df.columns
    #f,ax=plt.subplots(1,2, figsize=[8,3])
    #ax[0].plot(range(10),np.random.random(10))
    #ax[1].plot(range(10),np.random.random(10))
    #ax[0].set_ylabel("asdg")
    #ax[1].set_ylabel("sfgasd")
    #df.groupby('style').count()['climbid'].plot(kind='pie', ax=ax[0])
    #ax[0].set_ylabel("")
    #ax[0].set_title('climb type breakdown')
    #df.groupby('grade').count()['climbid'].plot(kind='bar', ax=ax[1])
    #ax[1].set_ylabel("")
    #ax[1].set_title('climb grade breakdown')
    #save2plotly(f, 'tempplot')
    pass