# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 09:12:37 2015

@author: amyskerry
"""
from flask import current_app, render_template
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
import numpy as np
import pandas as pd
import pickle
import json
from flask import jsonify
import home as hf
import warnings
import climb as cf
import os
from sqlalchemy import and_
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import between
import sys
import timeit
from collections import OrderedDict
from config import fulldir

sys.path.append(fulldir)
import antools.randomstuff as rd



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
        udict['Unknown Area']
    udict['region'] = db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().region
    udict['country'] = db.session.query(AreaTable).filter_by(areaid=udict['mainarea']).first().country
    return udict


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
            if 'newuser' in udict.keys() and udict['newuser'] == True:
                try:
                    featdict = current_app.modeldicts['feats_%s' % int(userid)]
                    labels =featdict.keys()
                    print "A"
                    print labels
                    labels.remove('flake')
                    labels.remove('cracks')
                    corrs = [float(featdict[l]) for l in labels]
                    corrs = [(c - 2) / 2 for c in corrs]
                    sems = [0 for c in corrs]
                except:
                    usdf = getuserstarsbywords(sdf, cdf, userid, current_app.askfeatures, blockterms=rd.blockterms)
                    usdf = usdf[[col for col in usdf.columns if len(usdf[col].unique()) != 1 or col == 'starsscore']]
                    print "B"
                    print usdf.columns
                    if len(usdf['starsscore'].unique()) == 1:
                        fakingit=True
                        usdf.iloc[0, :]['starsscore'] = 1
                    else:
                        fakingit=False
                    corrs, labels, sems = getuserpredictors(usdf)
                    if fakingit:
                        print "faking it"
                        corrs=[0+np.random.choice(np.arange(-0.05,.05,.001)) for c in corrs]
            else:
                usdf = getuserstarsbywords(sdf, cdf, userid, current_app.askfeatures, blockterms=rd.blockterms)
                usdf = usdf[[col for col in usdf.columns if len(usdf[col].unique()) != 1 or col == 'starsscore']]
                print "C"
                print usdf.columns
                fakingit=False
                if len(usdf['starsscore'].unique()) == 1:
                    fakingit=True
                    usdf.iloc[0, :]['starsscore'] = 1
                else:
                    fakingit=False
                corrs, labels, sems = getuserpredictors(usdf)
                if fakingit:
                    print "faking it"
                    corrs=[0+np.random.choice(np.arange(-0.05,.05,.001)) for c in corrs]
        except:
            warnings.warn("user star df/correlations failed")
        title = "Route Preferences for %s" % udict['name']
        title = "Preference Scores"
        djsons.append(pushdata(corrs, sems, labels, title, '', '', "plotcontainer"))
    except:
        djsons = []
        warnings.warn("plot failed")
    return djsons


def getuserrecs(udict, db, area, gradeshift, sport, trad, boulder):
    userid = udict['climberid']
    climbids = getuserrecommendedclimbs(udict, db, area, gradeshift, sport, trad, boulder)
    climbobjs = db.session.query(ClimbTable).filter(ClimbTable.climbid.in_(climbids)).all()
    recclimbs = [cf.getclimbdict(c, db) for c in climbobjs]
    for d in recclimbs:
        del d['_sa_instance_state']
    return recclimbs


def get_stylelist(sport, trad, boulder):
    styles = []
    if sport: styles.append('Sport');
    if trad: styles.append('Trad');
    if boulder: styles.append('Boulder')
    return styles


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


def getcandidates(udict, db, area, gradeshift, styles):
    try:
        styles = styles.split(', ')
    except:
        warnings.warn("styles already a list")
    graderanges = {}
    for style in ('Sport', 'Trad', 'Boulder'):
        graderanges[style] = getgraderange(udict, db, gradeshift, style)
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


def getuserrecommendedclimbs(udict, db, area, gradeshift, sport, trad, boulder):
    styles = get_stylelist(sport, trad, boulder)
    candidates = getcandidates(udict, db, area, gradeshift, styles)
    if len(candidates) == 0:
        candidates = getcandidates(udict, db, area, gradeshift,
                                   ['Sport', 'Trad', 'Boulder'])  #if no matches, generalize to all styles
    candidates = [cf.getclimbdict(c, db) for c in candidates]
    trainedclfdict = loadtrainedmodel(udict)
    classorder = list(trainedclfdict['clf'].classes_)
    classdict = {pred: classorder.index(pred) for pred in [1, 2, 3, 4] if pred in classorder}
    Xdf = pd.read_sql("SELECT * from final_X_matrix", db.engine, index_col='index')
    datadict = {'pred': [], 'prob': [], 'climbid': [], 'style': [], 'mainarea': [], 'grade': [], 'hit': []}
    for climb in candidates:
        datadict = scoreclimb(climb, db, Xdf, udict, trainedclfdict, datadict, classdict)
    preddf = pd.DataFrame(data=datadict)
    preddf = preddf.sort(columns=['pred', 'prob'], ascending=False)
    if len(preddf[(preddf['pred'] == 4) & (preddf['prob'] >= .9)]) > 10:
        preddf = preddf[(preddf['pred'] == 4) & (preddf['prob'] >= .9)]
        indices = preddf.climbid.values
        np.random.shuffle(indices)
        return indices[:10]
    else:
        return preddf.iloc[:10, :].climbid.values


def scoreclimb(climb, db, Xdf, udict, trainedclfdict, datadict, classdict):
    '''take individual candidate and score with model'''
    cid = climb['climbid']
    ufeatures = [f for f in trainedclfdict['finalfeats'] if f != 'avgstars']
    if 'other_avg' not in ufeatures:
        ufeatures = ['other_avg'] + ufeatures
    if cid in Xdf.index.values:
        row = Xdf.loc[cid, ufeatures]
        try:
            del row['climbid']
        except:
            pass
        featurevector = row.values
        pred = trainedclfdict['clf'].predict(featurevector)[0]
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


def getgraderange(udict, db, gradeshift, style):
    '''get range of rasonable grades'''
    g_median = udict['g_median_%s' % style]
    if style == 'Boulder':
        range = [g_median - 3, g_median + 3]
        range = [g + float(gradeshift) / 1.5 for g in range]
    else:
        range = [g_median - 5, g_median + 5]
        range = [g + float(gradeshift) for g in range]
    if range[1] < 0:
        range[1] = 1
    return range


def loadtrainedmodel(udict):
    '''load up pretrained model to run against candidates'''
    try:
        fname = 'user_%s_model.pkl' % (udict['climberid'])
        clf = current_app.modeldicts[fname]
    except:
        warnings.warn("%s not in modeldicts.keys()" % fname)
        modeldir = os.path.join(fulldir, 'data/models')
        try:
            with open(os.path.join(modeldir, fname), 'rb') as inputfile:
                clf = pickle.load(inputfile)
            warnings.warn("successfully loaded from file")
        except:
            warnings.warn("loading %s failed" % fname)
    return clf


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
    jsondict['xAxis'][0]['categories'] = [rd.labeldict[l] if l in rd.labeldict.keys() else l for l in labels]
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
