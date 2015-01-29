# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:12:37 2015

@author: amyskerry
"""
from flask import current_app
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
from sqlalchemy.sql.expression import between
import sys
import timeit
from collections import OrderedDict

rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
dirname=os.path.join(rootdir, 'Projects', 'cragcrunch/')
sys.path.append(dirname)
import antools
from config import rootdir, projectroot
import antools.randomstuff as rd



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
    sdf=pd.read_sql("SELECT * from stars_prepped where climber = '%s'" %userid, db.engine, index_col='index')
    userclimbs=sdf.climb.unique()
    userclimbstring=','.join([str(el) for el in userclimbs])
    cdf=pd.read_sql("SELECT * from climb_prepped where climbid in(%s)" %userclimbstring, db.engine, index_col='index')
    djsons=[]
    redfeatfile=os.path.join(dirname,'data','learnedfeatures.pkl')
    with open(redfeatfile, 'r') as inputfile:
        feats=pickle.load(inputfile)['reducedtextfeats']
    bterms=['easy_description','hard_description','clipping_description','gear_description','easy_commentsmerged','hard_commentsmerged','clipping_commentsmerged','gear_commentsmerged']
    usdf=getuserstarsbywords(sdf, cdf, userid, feats, blockterms=bterms)
    corrs, labels, sems=getuserpredictors(usdf)
    djsons.append(pushdata(corrs, sems, labels, 'Feature Preference', 'Climb Features', 'preference score', "plotcontainer0"))
    return djsons
    
def getuserrecs(udict, db, area, gradeshift, sport, trad, boulder):
    userid=udict['climberid']
    climbids=getuserrecommendedclimbs(udict, db, area, gradeshift, sport, trad, boulder)
    print "OUT"
    print timeit.default_timer()
    #climbids=[c['climbid'] for c in hf.gettopclimbs(db)]
    climbobjs=db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).all()
    recclimbs=[cf.getclimbdict(c, db) for c in climbobjs]
    for d in recclimbs:
        del d['_sa_instance_state']
    return recclimbs

def getuserrecommendedclimbs(udict, db, area, gradeshift, sport, trad, boulder):
    graderanges={}
    for style in ('Sport', 'Trad', 'Boulder'):
        graderanges[style]=getgraderange(udict,db, gradeshift, style)
    styles=[]
    if sport: styles.append('Sport');
    if trad: styles.append('Trad');
    if boulder: styles.append('Boulder')
    candidates=[]
    print timeit.default_timer()
    for style in styles:
        thesecandidates=db.session.query(ClimbTable).filter(and_((ClimbTable.mainarea==area), ClimbTable.numerizedgrade.between(graderanges[style][0],graderanges[style][1]), (ClimbTable.style == style))).all()
        candidates.extend([cf.getclimbdict(c, db) for c in thesecandidates])
    trainedclfdict, modeltype=loadtrainedmodel(udict) ##add logic for new users here
    classorder=list(trainedclfdict['clf'].classes_)
    classdict={pred:classorder.index(pred) for pred in [1,2,3,4]}
    print "processing %s candidate regions" %len(candidates)

    if modeltype=='full':
        Xdf = pd.read_sql("SELECT * from final_X_matrix", db.engine, index_col='index')
    else:
        Xdf = pd.read_sql("SELECT * from final_X_matrix_red", db.engine, index_col='index')
    datadict={'pred':[], 'prob':[],'climbid':[],'style':[],'mainarea':[],'grade':[],'hit':[]}
    print "A"
    print timeit.default_timer()
    for climb in candidates:
        datadict=scoreclimb(climb, db, Xdf, udict, trainedclfdict, datadict, classdict)
    print "B"
    print timeit.default_timer()
    preddf=pd.DataFrame(data=datadict)
    preddf=preddf.sort(columns=['pred','prob'], ascending=False)
    if len(preddf[(preddf['pred']==4) & (preddf['prob']>=.9)])>10:
        preddf=preddf[(preddf['pred']==4) & (preddf['prob']>=.9)]
        indices=preddf.climbid.values
        np.random.shuffle(indices)
        return indices[:10]
    else:
        return preddf.iloc[:10,:].climbid.values

def scoreclimb(climb,db, Xdf, udict, trainedclfdict, datadict, classdict):
    '''take individual candidate and score with model'''
    cid=climb['climbid']
    ufeatures= trainedclfdict['finalfeats']
    if cid in Xdf.index.values:
        row=Xdf.loc[cid,['climbid']+ufeatures]
        del row['climbid']
        featurevector=row.values
        pred=trainedclfdict['clf'].predict(featurevector)[0]
        datadict['pred'].append(pred)
        datadict['prob'].append(trainedclfdict['clf'].predict_proba(featurevector)[0][classdict[pred]])
        datadict['climbid'].append(cid)
        datadict['style'].append(climb['style'])
        datadict['mainarea'].append(['mainarea'])
        datadict['grade'].append(['grade'])
        #ultimately want a record of climbs the user has done so that we can exclude them, but I'm leaving this out for speed reasons right now
        #hit = len(pd.read_sql("SELECT * from hits_prepped where climber = %s and climb = %s" %(udict['climberid'],cid), db.engine, index_col='index'))
        #datadict['hit'].append(hit)
        datadict['hit'].append(0)
    return datadict

def getmainareaoptions(db):
    localdf=pd.read_sql("SELECT * from area_prepped where country = 'USA'", db.engine, index_col='index').sort(columns='name')
    regions=[x for x in localdf.region.unique() if x !='World']
    regionids=[float(localdf[localdf['name']==r].areaid.values[0]) for r in regions]
    areadf=pd.read_sql("SELECT * from area_prepped where area in (%s)" %','.join(str(r) for r in regionids), db.engine, index_col='index').sort(columns='name')
    areas = areadf['areaid'].values
    names = areadf['name'].values
    return OrderedDict((float(aid),str(names[aidn])) for aidn,aid in enumerate(areas) if '*' not in str(names[aidn]))

def getgraderange(udict,db, gradeshift, style):
    g_min = udict['g_min_%s' %style]
    g_max = udict['g_max_%s' %style]
    g_median = udict['g_median_%s' %style]
    if style=='Boulder':
        range=[g_median-3, g_median+3]
        range=[g+float(gradeshift)/1.5 for g in range]
    else:
        range=[g_median-5, g_median+5]
        range=[g+float(gradeshift) for g in range]
    if range[1]<0:
        range[1]=1
    return range

def loadtrainedmodel(udict):
    try:
        fname='user_%s_model.pkl'%(udict['climberid'])
        clf=current_app.modeldict[fname]
        return clf, 'full'
    except:
        fname='newuser_%s_model.pkl'%(udict['climberid'])
        clf=current_app.modeldict[fname]
        return clf, 'reduced'


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


def getuserstarsbywords(sdf, cdf, climberid, terms, blockterms=[]):
    terms=[t for t in terms if t not in blockterms]
    sdf=sdf[sdf['climber']==climberid]
    sdf=pd.merge(sdf, cdf, left_on='climb', right_on=['climbid'], how='left')
    dcols=[c for c in terms if '_description' in c]
    dlen=np.array([len(x) if isinstance(x,str) else 0 for x in sdf.description.values])
    ccols=[c for c in terms if '_commentsmerged' in c]
    clen=np.array([len(x) if isinstance(x,str) else 0 for x in sdf.commentsmerged.values])
    dvals=(sdf[dcols].values.T/dlen).T
    cvals=(sdf[ccols].values.T/clen).T
    mvals=np.nanmean([cvals,dvals], axis=0)
    terms=list(set([t[:t.index('_')] for t in terms if '_' in t]))
    ndf=pd.DataFrame(index=sdf['climb'], data=mvals, columns=terms)
    ndf['starsscore']=sdf['starsscore'].values
    return ndf[['starsscore']+terms]

def standarderrorcorr(r,n):
    return (1-r**2)/np.sqrt(n-1)

def getuserpredictors(usdf):
    predictions=usdf.corr().loc['starsscore'][1:].dropna()
    corrs=predictions.values
    labels=predictions.index.values
    sems=[standarderrorcorr(r, len(usdf)) for r in corrs]
    return corrs, labels, sems
