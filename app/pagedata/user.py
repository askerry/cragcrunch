# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:12:37 2015

@author: amyskerry
"""
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
import numpy as np
import pandas as pd
import viz
import misc
import json
from flask import jsonify
import home as hf
import climb as cf

from config import rootdir


##################################################
#                User Page Functions             #
##################################################

def getuserdict(u,db):
    udict=u.__dict__
    udict['climberid']=int(udict['climberid'])
    try:
        udict['age']="%s years" %int(udict['age'])
    except:
        udict['age']=''
    try:
        udict['gender']={'F':'Male', 'M':'Male'}[udict['gender']]
    except:
        udict['gender']=''
    udict['mainarea_name']=db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().name
    udict['region']=db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().region
    udict['country']=db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().country
    return udict
    
def getuserplots(udict,db):
    '''
    userid=udict['climberid']
    userstars=db.session.query(StarsTable).filter_by(climber=userid).all()
    sdf=misc.convertsqlobj2df(userstars)
    userclimbs=sdf.climb.unique()
    climbdata=db.session.query(ClimbTable).all()
    cdf=misc.convertsqlobd2df(climbdata)
    for t in misc.termtypes.keys():
        ndf=getuserstarsbywords(sdf, cdf, userid, misc.terms)
        usdf=getuserstarsbywords(sdf, cdf, userid, misc.termtypes[t])
        f,ax, corrs, labels, sems=getuserpredictors(usdf,t, minn=6)
    '''
    plotdata=demofig()
    print plotdata
    return plotdata
    
def getuserrecs(udict, db):
    userid=udict['climberid']
    #climbids=getusersimilarclimbs(udict, db)
    climbids=[c['climbid'] for c in hf.gettopclimbs(db)]
    climbobjs=db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).all()
    recclimbs=[cf.getclimbdict(c, db) for c in climbobjs]
    return recclimbs

import matplotlib.pyplot as plt
import seaborn as sns
import mpld3

def demofig():
    means=[3,4,5,2]
    sems=[[2,4],[3,5],[4.5,5.7],[1.5,2.3]]
    labels=['green','blue','orange','pink']
    plottitle='HIIII'
    xlabel='my x label'
    ylabel='my y label'
    djson=pushdata(means, sems, labels, plottitle, xlabel, ylabel)
    print djson
    return djson

def demofig1():
    corrs=[1,2,3,4,5,4,3,2,6,7]
    sems=[.1,.2,.3,.4,.5,.1,.2,.3,.1,.6]
    labels=['a','b','c','d','e','f','g','h','i','j']
    f,ax=plt.subplots(figsize=[4,3])
    ax.bar(range(len(corrs)), corrs, yerr=sems)
    ax.set_xlim([0,len(corrs)])
    ax.set_xticks(np.arange(len(corrs))+.5)
    ax.set_xticklabels(labels, rotation=90)
    ax.set_ylabel('preference score')
    ax.set_xlabel('x label')
    ax_fmt = HelloWorld()
    mpld3.plugins.connect(f, ax_fmt)
    return mpld3.fig_to_html(f)


def makejsontemplate():
    errdata={"name": "variable error","type": "errorbar","yAxis": 0,"data": [[48, 51], [68, 73], [92, 110], [128, 136]],"tooltip": {"pointFormat": "(error range: {point.low}-{point.high} mm)<br/>"}}
    coldata={"name": "variable","type": "column","yAxis": 0, "data": [49.9, 71.5, 106.4, 129.2],"tooltip": {"pointFormat": '<span style="font-weight: bold; color: {series.color}">{series.name}</span>: <b>{point.y:.1f} mm</b>'}}
    series=[coldata, errdata]
    jsondict={"chart": {"zoomType": "xy"},"title": {"text": " default title"},"xAxis": [{"categories": ["a", "b", "c", "d"]}],"yAxis": [{"labels": {"style": {"color": 'red'}},"title": {"text": "variable name","style": {"color": 'blue'}}}],"tooltip": {"shared": True}, 'series':series}
    return jsondict
def pushdata(means, sems, labels, title, xlabel, ylabel):
    jsondict=makejsontemplate()
    jsondict['series'][0]['data']=means
    jsondict['series'][1]['data']=sems
    jsondict['xAxis'][0]['categories']=labels
    jsondict['title']['text']=title
    jsondict['yAxis'][0]['title']['text']=ylabel
    jsondict['yAxis'][0]['title']['text']=xlabel
    djson=json.dumps(jsondict)
    return djson


def getuserstarsbywords(sdf, cdf, climberid, terms):
    sdf=sdf[sdf['climber']==climberid]
    sdf=pd.merge(sdf, cdf, left_on='climb', right_on=['climbid'], how='left')
    dcols=[c+'_description' for c in terms]
    dlen=np.array([len(x) if isinstance(x,str) else 0 for x in sdf.description.values])
    ccols=[c+'_commentsmerged' for c in terms]
    clen=np.array([len(x) if isinstance(x,str) else 0 for x in sdf.commentsmerged.values])
    dvals=(sdf[dcols].values.T/dlen).T
    cvals=(sdf[ccols].values.T/clen).T
    mvals=np.nanmean([cvals,dvals], axis=0)
    ndf=pd.DataFrame(index=sdf['climb'], data=mvals, columns=terms)
    ndf['starsscore']=sdf['starsscore'].values
    return ndf[['starsscore']+terms]
def standarderrorcorr(r,n):
    return (1-r**2)/np.sqrt(n-1)
def getuserpredictors(usdf,t,minn=6):
    predictions=usdf.corr().loc['starsscore'][1:].dropna()
    corrs=predictions.values
    labels=predictions.index.values
    sems=[standarderrorcorr(r, len(usdf)) for r in corrs]
    if len(labels)>4:
        f,ax=plt.subplots(figsize=[4,3])
        ax.bar(range(len(corrs)), corrs, yerr=sems)
        ax.set_xlim([0,len(corrs)])
        ax.set_xticks(np.arange(len(corrs))+.5)
        ax.set_xticklabels(labels, rotation=90)
        ax.set_ylabel('preference score')
        ax.set_xlabel(t)
        sns.despine()
        plt.tight_layout()
    else:
        f,ax=[],[]
    return f,ax, corrs, labels, sems


import mpld3.plugins
class HelloWorld(mpld3.plugins.PluginBase):  # inherit from PluginBase
    """Hello World plugin"""

    JAVASCRIPT = """
    mpld3.register_plugin("helloworld", HelloWorld);
    HelloWorld.prototype = Object.create(mpld3.Plugin.prototype);
    HelloWorld.prototype.constructor = HelloWorld;
    function HelloWorld(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    HelloWorld.prototype.draw = function(){
        // FIXME: this is a very brittle way to select the y-axis element
        var ax = this.fig.axes[0].elements[1];

        // see https://github.com/mbostock/d3/wiki/Formatting#d3_format
        // for d3js formating documentation
        ax.axis.tickFormat(d3.format("d"));

        // TODO: use a function for tick values that
        // updates when values pan and zoom
        ax.axis.tickValues([1,100,1000]);

        // HACK: use reset to redraw figure
        this.fig.reset();
    }
    """
    def __init__(self):
        self.dict_ = {"type": "helloworld"}