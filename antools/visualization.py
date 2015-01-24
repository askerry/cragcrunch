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
    plt.figure(figsize=[4,3.5])
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
    plt.xticks(np.arange(len(labels))+.5,labels)
    plt.yticks(np.arange(len(labels))+.5,labels, rotation=90)
    plt.colorbar()
    
def customlegend(colordict, loc=[1,0], alpha=1):
    recs=[]
    keys=colordict.keys()
    for key in keys:
        recs.append(Rectangle((0,0),1,1,fc=colordict[key]))
    return plt.legend(recs, keys, loc=loc)
    
def alphapallete(palletename, n_colors, alpha):
    return [(tup[0],tup[1],tup[2], alpha) for tup in sns.color_palette(palletename, n_colors=n_colors)]
    

#mapping
    
def mapfeature(coords, coordlabels, colordict, center=(33.73,-100.45),size='country'):
    dmap=mapit(coords=center, size='country')
    for coordn, coord in enumerate(coords):
        if coordlabels[coordn] in colordict.keys():
            color=colordict[coordlabels[coordn]]
        else:
            color=(.3,.3,.3,.4)
        dmap=plotloc(dmap, coords=coord, markersize=5, color=color)
    customlegend(colordict)
    return dmap
    
def legendhack(colordict):
    keys=colordict.keys()
    print keys
    sns.palplot([colordict[key] for key in keys])    
    
def prepmapvars(mapdf, featurename=None):
    mapdf=mapdf.loc[~np.isnan(mapdf['latitude'])]
    mapdf=mapdf.loc[[val!=None for val in mapdf[featurename].values]]
    try:
        mapdf=mapdf.loc[~np.isnan(mapdf[featurename])]
    except:
        pass
    coords=[(lat, mapdf.longitude.values[latn]) for latn,lat in enumerate(mapdf.latitude.values)]
    if featurename:
        coordlabels=mapdf[featurename].values
    else:
        coordlabels=[1 for el in mapdf.values]
    labels=list(set(coordlabels))
    labels.sort()
    if type(labels[0]) in (str, np.string_):
        colors=alphapallete('Set1', len(labels), .7)
    else:
        colors=alphapallete('cool', len(labels), .6)
    colordict=OD([(label,colors[labeln]) for labeln,label in enumerate(labels)])
    return coords, coordlabels, colordict    

def mapit(lat=None, lon=None, coords=None, size='city', w=None, h=None, figsize=[20,6], projection='mill', bluemarble=False, landcolor=(.8,.5,.2,.03), lakecolor=(0,.1,.6,.1), resolution='i', fillcolor=(0,.1,.6,.1)):
    f=plt.figure(figsize=figsize)
    if coords:
        lat,lon=coords
    if not w and not h:
        if size=='city':
            w,h=.40,.20
        if size=='state':
            w,h,=8.0,4.0
        if size=='country':
            w,h,=60.0,30.0
        if size=='world':
            w,h=None,None
    elif not w:
        w=h
    elif not h:
        h=w
    if w:
        m=Basemap(projection=projection, lat_0=lat, lon_0=lon, llcrnrlat=lat-h/2, llcrnrlon =lon-w/2, urcrnrlat=lat+h/2, urcrnrlon=lon+w/2, resolution = resolution)
    else:
        m=Basemap(projection=projection, lat_0=lat, lon_0=lon, resolution = resolution)
    m.drawcoastlines()
    m.drawcountries()
    m.drawrivers()
    m.drawstates()
    if bluemarble:
        # display blue marble image (from NASA) as map background
        m.bluemarble()
    else:
        if fillcolor:
            m.drawmapboundary(fill_color=fillcolor)
        m.fillcontinents(color = (1,1,1), lake_color = (1,1,1))
        m.fillcontinents(color = landcolor, lake_color = lakecolor)
     
    #longmarkers=worldmap.drawmeridians(np.arange(0, 360, 30))
    #latmarkers=worldmap.drawparallels(np.arange(-90, 90, 30))
    return m
def plotloc(mapbase, lat=None, lon=None, marker='o', color='b', markersize=10, coords=None, label=None):
    if coords:
        lat,lon=coords
    elif not lat:
        lat=np.mean([mapbase.latmin, mapbase.latmax])
        marker='+'
    elif not lon:
        lon=np.mean([mapbase.lonmin, mapbase.lonmax])
        marker='+'
    x,y=mapbase(lon,lat)
    mapbase.plot(x, y, marker, color=color, markersize=markersize)
    if label:
        plt.text(x,y,label)
    return mapbase
