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
    userid=udict['climberid']
    userstars=db.session.query(StarsTable).filter_by(climber=userid).all()
    sdf=misc.convertsqlobj2df(userstars)
    userclimbs=sdf.climb.unique()
    climbdata=db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(userclimbs)).all()
    cdf=misc.convertsqlobj2df(climbdata)
    djsons=[]
    for tn,t in enumerate(['hold types','face descriptions','ease factors','safety factors']):
        usdf=getuserstarsbywords(sdf, cdf, userid, misc.termtypes[t])
        corrs, labels, sems=getuserpredictors(usdf,t, minn=6)
        plotid="plotcontainer%s" %tn
        djsons.append(pushdata(corrs, sems, labels, '', t, 'preference score', plotid))
    return djsons
    
def getuserrecs(udict, db):
    userid=udict['climberid']
    #climbids=getusersimilarclimbs(udict, db)
    climbids=[c['climbid'] for c in hf.gettopclimbs(db)]
    climbobjs=db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).all()
    recclimbs=[cf.getclimbdict(c, db) for c in climbobjs]
    return recclimbs



def makejsontemplate():
    errdata={"name":"95% CI", "type": "errorbar","data": [[48, 51], [68, 73], [92, 110], [128, 136]]}
    coldata={"name":"Preference Score","type":"column","data": [49.9, 71.5, 106.4, 129.2]}
    series=[coldata, errdata]
    jsondict={}
    jsondict["chart"]={"type":"errorbar", "renderTo":"plotcontainer", "backgroundColor":'#55FF88'}
    for item in {'margin': [50, 20, 50, 50]}.items():
        jsondict["chart"][item[0]]=item[1]
    jsondict["series"]=series
    jsondict["legend"]={'enabled':False}
    jsondict["exporting"]= {"enabled": False }
    jsondict["credits"]={'enabled':False}
    jsondict["title"]={"text": "default title"}
    jsondict["xAxis"]=[{"categories": ["a", "b", "c", "d"],'labels':{'rotation':-90}, "title": {"text": "xlabel","style": {"color": 'black'}}}]
    jsondict["yAxis"]=[{"labels": {"style": {"fontSize":"8px","fontFamily": 'Verdana, sans-serif',"color": 'black'}}, "max":-1, "max":1, "title": {"text": "variable name","style": {"color": 'black'}}}]

    return jsondict
def pushdata(means, sems, labels, title, xlabel, ylabel, plotid):
    jsondict=makejsontemplate()
    jsondict['chart']['renderTo']=plotid
    jsondict['series'][0]['data']=list(means)
    jsondict['series'][1]['data']=[[m-2*sems[mn],m+2*sems[mn]] for mn,m in enumerate(means)]
    jsondict['xAxis'][0]['categories']=list(labels)
    jsondict['title']['text']=title
    jsondict['yAxis'][0]['title']['text']=ylabel
    jsondict['xAxis'][0]['title']['text']=xlabel
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
    return corrs, labels, sems

