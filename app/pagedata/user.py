# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:12:37 2015

@author: amyskerry
"""
from flask import current_app, render_template
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable, ProfileTable, HitsTable
import numpy as np
import pandas as pd
import pickle
import json
from flask import jsonify
import home as hf
import warnings
import climb as cf
import scipy.stats
import os
from sqlalchemy import and_
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import between
import sys
import timeit
from collections import OrderedDict
from config import fulldir

sys.path.append(fulldir)
import rec.scoring as scoring
import utilities.randomdata as rd




# #################################################
#                User Page Functions             #
##################################################

def getuserdict(u, db):
    udict = u.__dict__
    udict['climberid'] = int(udict['climberid'])
    try:
        udict['age'] = "%s years" % int(udict['age'])
    except:
        udict['age'] = ''
    try:
        udict['gender'] = {'F': 'Male', 'M': 'Male'}[udict['gender']]
    except:
        udict['gender'] = ''
    try:
        udict['mainarea_name'] = db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().name
    except:
        udict['mainarea_name']='Unknown Area'
    udict['region'] = db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().region
    udict['country'] = db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().country
    return udict

def load_preferences(db, userid, attributes):
    prefs=json.loads(db.session.query(ProfileTable).filter_by(userid=userid).first().preferences)
    return {key: prefs[key] for key in attributes}

def getuserplots(udict, db):
    userid = udict['climberid']
    prefs=json.loads(db.session.query(ProfileTable).filter_by(userid=userid).first().preferences, object_pairs_hook=OrderedDict)
    labels=prefs.keys()
    try:
        corrs=[prefs[attr] for attr in labels]
        #zeros look weird
        corrs=[c if c!=0 else np.random.choice([.08, .03, .1, -.01, -.04, -.7]) for c in corrs]
        sems = [0 for c in corrs]
        title = "Route Preferences for %s" % udict['name']
        title = "Preference Scores"
        djsons=[pushdata(corrs, sems, labels, title, '', '', "plotcontainer")]
    except:
        djsons = []
        warnings.warn("plot failed")
    return djsons
'''
def getuserplots(udict, db):
    userid = udict['climberid']
    sdf = pd.read_sql("SELECT * from stars_prepped where climber = '%s'" % userid, db.engine, index_col='index')
    userclimbs = sdf.climb.unique()
    userclimbstring = ','.join([str(el) for el in userclimbs])
    try:
        try:
            cdf = pd.read_sql("SELECT * from climb_prepped where climbid in(%s)" % userclimbstring, db.engine,
                              index_col='index')
        except:
            warnings.warn("climb selection failed")
        djsons = []
        try:
            if 'newuser' in udict and udict['newuser'] == True:
                try:
                    featdict = current_app.modeldicts['feats_%s' % int(userid)]
                    labels =featdict.keys()
                    labels.remove('flake')
                    labels.remove('cracks')
                    corrs = [float(featdict[l]) for l in labels]
                    corrs = [(c - 2) / 2 for c in corrs]
                    sems = [0 for c in corrs]
                except:
                    usdf = getuserstarsbywords(sdf, cdf, userid, current_app.askfeatures, blockterms=rd.blockterms)
                    usdf = usdf[[col for col in usdf.columns if len(usdf[col].unique()) != 1 or col == 'starsscore']]
                    if len(usdf['starsscore'].unique()) == 1:
                        fakingit=True
                        usdf.iloc[0, :]['starsscore'] = 1
                    else: fakingit=False
                    corrs, labels, sems = getuserpredictors(usdf)
                    if fakingit: corrs=[0+np.random.choice(np.arange(-0.05,.05,.001)) for c in corrs]
            else:
                usdf = getuserstarsbywords(sdf, cdf, userid, current_app.askfeatures, blockterms=rd.blockterms)
                usdf = usdf[[col for col in usdf.columns if len(usdf[col].unique()) != 1 or col == 'starsscore']]
                fakingit=False
                if len(usdf['starsscore'].unique()) == 1:
                    fakingit=True
                    usdf.iloc[0, :]['starsscore'] = 1
                else: fakingit=False
                corrs, labels, sems = getuserpredictors(usdf)
                if fakingit: corrs=[0+np.random.choice(np.arange(-0.05,.05,.001)) for c in corrs]
        except:
            warnings.warn("user star df/correlations failed")
        title = "Route Preferences for %s" % udict['name']
        title = "Preference Scores"
        djsons.append(pushdata(corrs, sems, labels, title, '', '', "plotcontainer"))
    except:
        djsons = []
        warnings.warn("plot failed")
    return djsons
'''

def getuserrecs(udict, db, area, grade, sport, trad, boulder):
    userid = udict['climberid']
    climbids = getuserrecommendedclimbs(udict, db, area, grade, sport, trad, boulder)
    climbobjs = db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).all()
    recclimbs = [cf.getclimbdict(c, db) for c in climbobjs]
    for d in recclimbs:
        del d['_sa_instance_state']
    return recclimbs

def updatepref(db, userid, feature, value):
    matchuser=db.session.query(ProfileTable).filter_by(userid=userid).first()
    if matchuser is not None:
        u=matchuser
        pref=json.loads(u.preferences)
        pref[feature]=value
        u.preferences=json.dumps(pref)
        db.session.add(u)
        db.session.flush()
        db.session.commit()

def get_stylelist(sport, trad, boulder):
    styles = []
    if sport: styles.append('Sport');
    if trad: styles.append('Trad');
    if boulder: styles.append('Boulder')
    return styles

'''
def addstar(db, userid, username, climbid, climbname, rating):
    matchstar=db.session.query(StarsTable).filter(and_(StarsTable.climber==userid, StarsTable.climb==climbid)).first()
    if matchstar is not None:
        nstar=matchstar
        nstar.starsscore=rating
    else:
        nstar = StarsTable(climber=str(userid), starsscore=rating, climb=climbid, name="%s_%s" % (username, climbname))
        maxstarid = float(db.session.query(func.max(StarsTable.starid)).first()[0])
        nstar.starid = maxstarid + 1
    db.session.add(nstar)
    db.session.flush()
    db.session.commit()
'''

def derive_prefs(db, userid, attr):
    star_entries=db.session.query(StarsTable).filter_by(climber=userid).all()
    starids=[entry.climb for entry in star_entries]
    stars=[entry.starsscore for entry in star_entries]
    feats={key:[] for key in attr}
    if len(starids)>0:
        for climb in starids:
            result=db.session.query(ClimbTable).filter_by(climbid=climb).first()
            for key in attr:
                feats[key].append(getattr(result, 't_'+key))
        pref_dict={}
        for key in attr:
            corr=scipy.stats.pearsonr(stars, feats[key])[0]
            if np.isnan(corr):
                corr=0
            pref_dict[key]=corr
    else:
        pref_dict={key:0 for key in attr}
    return pref_dict

def add_to_profile(db, uobj, password):
    prefs=json.dumps(derive_prefs(db, uobj.climberid, current_app.attributes))
    nuser = ProfileTable(userid=uobj.climberid, name=uobj.name, password=password, region= uobj.region, mainarea = uobj.mainarea, preferences=prefs)
    db.session.add(nuser)
    db.session.flush()
    db.session.commit()

def getcandidates(udict, db, area, grade, styles):
    try:
        styles = styles.split(', ')
    except:
        warnings.warn("styles already a list")
    graderanges = {}
    for style in ('Sport', 'Trad', 'Boulder'):
        graderanges[style] = getgraderange(udict, db, style=style, gradepercent=(float(grade)-12)/12)
    candidates = []
    for style in styles:
        thesecandidates = [c for c in db.session.query(ClimbTable).filter(and_((ClimbTable.mainarea == area),
                                                                               ClimbTable.numerizedgrade.between(
                                                                                   graderanges[style][0],
                                                                                   graderanges[style][1]),
                                                                               (ClimbTable.style == style))).all()]
        candidates.extend(thesecandidates)

    if len(candidates)==0:
        for style in styles:
            thesecandidates = [c for c in db.session.query(ClimbTable).filter(and_((ClimbTable.mainarea == area),
                                                                               ClimbTable.numerizedgrade.between(
                                                                                   graderanges[style][0]-5,
                                                                                   graderanges[style][1]+5),
                                                                               (ClimbTable.style == style))).all()]
            candidates.extend(thesecandidates)
    return candidates

def getuserrecommendedclimbs(udict, db, area, grade, sport, trad, boulder):
    styles = get_stylelist(sport, trad, boulder)
    print udict, area, grade, styles
    candidates = getcandidates(udict, db, area, grade, styles)
    if len(candidates) == 0:
        candidates = getcandidates(udict, db, area, grade,
                                   ['Sport', 'Trad', 'Boulder'])  #if no matches, generalize to all styles
    candidates = [cf.getclimbdict(c, db) for c in candidates]
    candidates={c['climbid']:c for c in candidates}
    datadict = {'score': [], 'climbid': [], 'style': [], 'mainarea': [], 'grade': [], 'hit': []}
    userclimbs, prefs, allstars=rec_preloads(db, udict, candidates)
    print len(candidates)
    for climbid in candidates.keys():
        climb=candidates[climbid]
        for var in ['climbid', 'style', 'mainarea', 'grade']:
            datadict[var].append(climb[var])
        datadict['score'].append(scoring.finalscore(db, udict, climbid, candidates, current_app.attributes, userclimbs, prefs, allstars))
        #match=len(db.session.query(HitsTable).filter(and_(HitsTable.climber==udict['climberid'], HitsTable.climb==climb['climbid'])).all())>0
        match=0
        datadict['hit'].append(match)
    preddf = pd.DataFrame(data=datadict)
    preddf = preddf.sort(columns=['score'], ascending=False)
    return preddf.iloc[:10, :].climbid.values

def rec_preloads(db, udict, candidates):
    climbobjs=db.session.query(StarsTable).filter_by(climber=udict['climberid']).all()
    userclimbs={c.climb:c.starsscore for c in climbobjs}
    userobj=db.session.query(ProfileTable).filter_by(userid=udict['climberid']).first()
    prefs=json.loads(userobj.preferences)
    allstars={c:[] for c in candidates.keys()}
    for entry in db.session.query(StarsTable).filter(StarsTable.climb.in_(candidates.keys())).all():
        allstars[entry.climb].append({'climberid':entry.climber, 'starsscore':entry.starsscore})
    return userclimbs, prefs, allstars

def getmainareaoptions(db):
    '''get list of possible main areas'''
    localdf = pd.read_sql("SELECT * from area_prepped where country = 'USA'", db.engine, index_col='index').sort(
        columns='name')
    regions = [x for x in localdf.region.unique() if x != 'World']
    regionids = [float(localdf[localdf['name'] == r].areaid.values[0]) for r in regions]
    areadf = pd.read_sql("SELECT * from area_prepped where area in (%s)" % ','.join(str(r) for r in regionids),
                         db.engine, index_col='index').sort(columns='name')
    areas = areadf['areaid'].values
    names = areadf['name'].values
    return OrderedDict((float(aid), str(names[aidn])) for aidn, aid in enumerate(areas) if '*' not in str(names[aidn]))


def getgraderange(udict, db, style=None, gradepercent=None):
    '''get range of rasonable grades'''
    defaults={'Sport':41, 'Trad':31, 'Boulder':11}
    dgrade=defaults[style]
    if gradepercent is None:
        grade=dgrade
    else:
        grade=dgrade+gradepercent*dgrade
    if style == 'Boulder':
        range = [grade - 3, grade + 3]
    else:
        range = [grade - 5, grade + 5]
    if range[1] < 0:
        range[1] = 1
    return range


def makejsontemplate(plotstyle='horizontal'):
    '''make dummy template for highcharts'''
    if plotstyle == "horizontal":
        bartype = 'bar'
        rotation = 0
    else:
        bartype = 'column'
        rotation = -75
    errdata = {"name": "Standard Error", "type": "errorbar", "data": [[48, 51], [68, 73], [92, 110], [128, 136]]}
    coldata = {"name": "Preference Score", "type": bartype, "data": [49.9, 71.5, 106.4, 129.2]}
    series = [coldata, errdata]
    jsondict = {}
    jsondict["chart"] = {"type": "errorbar", "renderTo": "plotcontainer", "backgroundColor": '#FFFFFF'}
    for item in {'margin': [60, 10, 10, 130]}.items():
        jsondict["chart"][item[0]] = item[1]
    jsondict["series"] = series
    jsondict["legend"] = {'enabled': False}
    jsondict["exporting"] = {"enabled": False}
    jsondict["credits"] = {'enabled': False}
    jsondict["title"] = {"text": "default title"}
    jsondict["xAxis"] = [{"tickWidth": 0, "categories": ["a", "b", "c", "d"], 'labels': {'rotation': rotation},
                          "title": {"text": "xlabel", "style": {"color": 'black'}}}]
    jsondict["yAxis"] = [{"gridLineColor": '#FFFFFF', "max":.75, "min":-.75, "labels": {
    "style": {"fontSize": "8px", "fontFamily": 'Verdana, sans-serif', "color": 'white'}},
                          "title": {"text": "", "style": {"color": 'black'}}}]
    return jsondict


def pushdata(means, sems, labels, title, xlabel, ylabel, plotid):
    '''push actual data to the template'''
    jsondict = makejsontemplate()
    jsondict['chart']['renderTo'] = plotid
    jsondict['series'][0]['data'] = list(means)
    jsondict['series'][0]['tooltip'] = {'pointFormat': '<span>{series.name}</span>: {point.y:.2f}'}
    jsondict['series'][1]['data'] = [0 for el in means]
    #jsondict['series'][1]['data']=[[m-2*sems[mn],m+2*sems[mn]] for mn,m in enumerate(means)]
    jsondict['xAxis'][0]['categories'] = [rd.labeldict[l] if l in rd.labeldict else l for l in labels]
    jsondict['title']['text'] = title
    jsondict['yAxis'][0]['title']['text'] = ylabel
    jsondict['xAxis'][0]['title']['text'] = xlabel
    djson = json.dumps(jsondict)
    return djson


def getuserstarsbywords(sdf, cdf, climberid, terms, blockterms=[]):
    '''get df relating user star ratings and word frequencies'''
    terms = [t + '_description' for t in current_app.askfeatures_terms if t not in blockterms]
    sdf = sdf[sdf['climber'] == climberid]
    sdf = pd.merge(sdf, cdf, left_on='climb', right_on=['climbid'], how='left')
    dcols = [c for c in terms if '_description' in c]
    ndf = pd.DataFrame(index=sdf['climb'], data=sdf[dcols].values, columns=terms)
    ndf['starsscore'] = sdf['starsscore'].values
    return ndf[['starsscore'] + terms]


def standarderrorcorr(r, n):
    "standard error on a pearson r"
    return (1 - r ** 2) / np.sqrt(n - 1)


def getuserpredictors(usdf):
    '''compute correlations between individual features and climber ratings'''
    corr = usdf.corr()
    corr = corr.fillna(0)
    predictions = corr.loc['starsscore'][1:].dropna()
    corrs = predictions.values
    labels = predictions.index.values
    labels = [f[:f.index('_')] if '_' in f else f for f in labels]
    sems = [standarderrorcorr(r, len(usdf)) for r in corrs]
    return corrs, labels, sems
