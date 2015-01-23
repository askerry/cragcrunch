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
from config import projectroot
import pickle
import json
from flask import jsonify
import home as hf
import climb as cf
import os
from sqlalchemy import and_
import sys

rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
dirname=os.path.join(rootdir, 'Projects', 'cragcrunch/')
sys.path.append(dirname)

import antools


from config import rootdir, projectroot


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
    sdf=misc.convertsqlobj2df(userstars) ##WTF why did i do it this way
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
    
def getuserrecs(udict, db, area):
    userid=udict['climberid']
    climbids=getusersimilarclimbs(udict, db, area)
    #climbids=[c['climbid'] for c in hf.gettopclimbs(db)]
    climbobjs=db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).all()
    recclimbs=[cf.getclimbdict(c, db) for c in climbobjs]
    return recclimbs

def getusersimilarclimbs(udict, db, area):
    graderange=getgraderange(udict,db)
    candidates=db.session.query(ClimbTable).filter_by(mainarea=area).filter(and_(ClimbTable.numerizedgrade >= graderange[0], ClimbTable.numerizedgrade <= graderange[1])).all()
    candidates=[cf.getclimbdict(c, db) for c in candidates]
    trainedclfdict=loadtrainedmodel(udict)
    classorder=list(trainedclfdict['clf'].classes_)
    print "processing %s candidate regions" %len(candidates)
    Xdf = pd.read_sql("SELECT * from final_X_matrix", db.engine, index_col='index')
    preds,predprobas,climbs=[],[],[]
    for climb in candidates:
        cid=climb['climbid']
        if cid in Xdf.index.values:
            row=Xdf.loc[cid,:]
            del row['climbid']
            featurevector=row.values
            pred=trainedclfdict['clf'].predict(featurevector)[0]
            preds.append(pred)
            predprobas.append(trainedclfdict['clf'].predict_proba(featurevector)[0][classorder.index(pred)])
            climbs.append(cid)
    preddf=pd.DataFrame(data={'pred':preds, 'prob':predprobas,'climbid':climbs})
    preddf=preddf.sort(columns=['pred','prob'], ascending=False)
    print preddf.iloc[:10]
    return preddf.iloc[:10,:].climbid.values



'''
    #con=db.engine.connect()
    #result = con.execute("select * from final_X_matrix")
    trainedclfdict=loadtrainedmodel(udict)
    #features=trainedclfdict['features']
    #rlist=[]
    #for r in result:
    #    rlist.append({key:r[key] for key in features})
    #print len(rlist)
'''
def getgraderange(udict,db):
    g_min = udict['g_min']
    g_max = udict['g_max']
    g_median = udict['g_median']
    if g_max-g_min>16:
        range=[g_min, g_max]
    else:
        range=[g_median-8, g_median+8]
    return range


def loadtrainedmodel(udict):
    fname='user_%s_model.pkl'%(udict['climberid'])
    filename=os.path.join(rootdir,'Projects/cragcrunch/data','models',fname)
    with open(filename, 'r') as inputfile:
        trainedclfdict=pickle.load(inputfile)
    return trainedclfdict

def makejsontemplate():
    errdata={"name":"95% CI", "type": "errorbar","data": [[48, 51], [68, 73], [92, 110], [128, 136]]}
    coldata={"name":"Preference Score","type":"column","data": [49.9, 71.5, 106.4, 129.2]}
    series=[coldata, errdata]
    jsondict={}
    jsondict["chart"]={"type":"errorbar", "renderTo":"plotcontainer", "backgroundColor":'#FFFFFF'}
    for item in {'margin': [10, 10, 110, 65]}.items():
        jsondict["chart"][item[0]]=item[1]
    jsondict["series"]=series
    jsondict["legend"]={'enabled':False}
    jsondict["exporting"]= {"enabled": False }
    jsondict["credits"]={'enabled':False}
    jsondict["title"]={"text": "default title"}
    jsondict["xAxis"]=[{"categories": ["a", "b", "c", "d"],'labels':{'rotation':-75}, "title": {"text": "xlabel","style": {"color": 'black'}}}]
    jsondict["yAxis"]=[{"labels": {"style": {"fontSize":"8px","fontFamily": 'Verdana, sans-serif',"color": 'black'}}, "max":-1, "max":1, "title": {"text": "","style": {"color": 'black'}}}]

    return jsondict
def pushdata(means, sems, labels, title, xlabel, ylabel, plotid):
    jsondict=makejsontemplate()
    jsondict['chart']['renderTo']=plotid
    jsondict['series'][0]['data']=list(means)
    jsondict['series'][1]['data']=[[m-2*sems[mn],m+2*sems[mn]] for mn,m in enumerate(means)]
    jsondict['xAxis'][0]['categories']=list(labels)
    jsondict['title']['text']=title
    if plotid in ('plotcontainer0', 'plotcontainer2'):
        jsondict['yAxis'][0]['title']['text']=ylabel
        jsondict["chart"]['margin'][3]=40
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

