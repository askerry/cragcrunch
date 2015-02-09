__author__ = 'amyskerry'

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
from flask import current_app
import numpy as np
import pandas as pd
import json
from flask import jsonify, session
import home as hf
import climb as cf
import os
from sqlalchemy import and_
from sqlalchemy.sql import func
import warnings
import user as uf
import sys
from collections import OrderedDict
import pickle
import pdb
from config import fulldir, clf

sys.path.append(fulldir)
import antools.randomstuff as rd
import config


def getstates(db):
    '''get ordered dict of all possible states'''
    states = db.session.query(AreaTable).filter_by(region='World').all()
    states = {state.name: state.areaid for state in states if state.name != '* In Progress'}
    alphastates = sorted(states.keys())
    return OrderedDict((states[key], key) for key in alphastates if key != '* In Progress')


def getbouldergrades():
    return rd.listgrades_boulder


def getroutegrades():
    return rd.listgrades_route


def addtodb(db, request):
    '''take basic user info and save user to be'''
    styles = ['Sport, Trad, Boulder']
    name = request.form['name']
    if request.form['mainarea'] == 'Empty':
        mainarea = 0
    else:
        mainarea = float(request.form['mainarea'])
    nuser = ClimberTable(name=str(request.form['name']), gender=str(request.form['gender']), climbstyles=styles,
                         region=float(request.form['state']), mainarea=mainarea)
    if request.form['sportgrade'] == 'Empty':nuser.g_median_Sport = 39.0
    elif request.form['sportgrade'] < 8: nuser.g_median_Sport = 8
    else: nuser.g_median_Sport = float(request.form['sportgrade'])
    if request.form['tradgrade'] == 'Empty':nuser.g_median_Trad = 28.0
    elif request.form['tradgrade'] < 8: nuser.g_median_Trad = 8
    else:nuser.g_median_Trad = float(request.form['tradgrade'])
    if request.form['bouldergrade'] == 'Empty':nuser.g_median_Boulder = 14.0
    else:
        nuser.g_median_Boulder = float(request.form['bouldergrade'])
    nuser.climberid = 'Sport, Trad, Boulder'
    ndict = {item[0]: item[1] for item in nuser.__dict__.items()}
    maxclimberid = float(db.session.query(func.max(ClimberTable.climberid)).first()[0])
    nuser.climberid = maxclimberid + 1

    db.session.add(nuser)
    try:
        db.session.flush()
        db.session.commit()
    except:
        warnings.warn("DB flush fail for new user")
        querystr = "INSERT INTO climber_prepped (climberid, mainarea, name, url, gender, personal, age, favclimbs_parsed, favclimbs, interests, climbstyles, selfreportgrades, moreinfo, trad_l, trad_f, sport_l, sport_f, ice_l, ice_f, boulders, aid_l, aid_f, mixed_l, mixed_f, region, numhits, g_min_Sport, g_max_Sport, g_median_Sport, g_min_Trad, g_max_Trad, g_median_Trad, g_min_Boulder, g_max_Boulder, g_median_Boulder) VALUES (%s, %s, '%s', Null, '%s', Null, Null, Null, Null, Null, 'Sport, Trad, Boulder', Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, Null, %s, Null, Null, Null, %s, Null, Null, %s, Null, Null, %s)" % (
        nuser.climberid, nuser.mainarea, nuser.name, nuser.gender, nuser.region, nuser.g_median_Sport,
        nuser.g_median_Trad, nuser.g_median_Boulder)
        db.engine.execute(querystr)
        warnings.warn("raw SQL isert successful")
    ndict['climberid'] = int(float(nuser.climberid))
    session['userid']=int(float(nuser.climberid))
    del ndict['_sa_instance_state']
    return ndict


def addnewuserstars(db, userid, username, candidateids, Y):
    for cn, c in enumerate(candidateids):
        rating = Y[cn]
        cname = db.session.query(ClimbTable).filter_by(climbid=c).first().name
        uf.addstar(db, userid, username, c, cname, rating)


def modelnewuser(db, featdict, userid, username):
    '''take a dataframe of user expressed preferences and build a model of them'''
    Xdf = pd.read_sql("SELECT * from final_X_matrix", db.engine, index_col='index')  # load full sampleDF
    allfeatures = [x for x in Xdf.columns if x not in ('index', 'climbid', userid)]  # all features for full model
    userdict = session['stash'][str(userid)]
    candidates = uf.getcandidates(userdict, db, userdict['mainarea'], 0,
                                  userdict['climbstyles'][0])  # get initial set of candidates from users area
    candidateids = [float(cand.climbid) for cand in candidates]
    candidateids = [cand for cand in candidateids if cand in Xdf.climbid.values]
    if len(candidateids)==0:
        thesecandidates = [c for c in db.session.query(ClimbTable).filter_by(mainarea = userdict['mainarea']).all()]
        candidateids = [float(cand.climbid) for cand in thesecandidates]
        candidateids = [cand for cand in candidateids if cand in Xdf.climbid.values]
    candidateidstrs = [str(int(val)) for val in candidateids]
    features = ['avgstars'] + current_app.askfeatures
    try:
        samplesdf = pd.read_sql('select * from climb_prepped where climbid in (%s)' % ','.join(candidateidstrs), db.engine,
                                index_col='index')
    except:
        warnings.warn('failed to load constrained candidates. defaulting to full space')
        candidateids = Xdf.climbid.values[:30]
        candidateidstrs = [str(int(val)) for val in candidateids]
        samplesdf = pd.read_sql('select * from climb_prepped where climbid in (%s)' % ','.join(candidateidstrs), db.engine,
                                index_col='index')
    featdf = pd.read_sql('select * from featranges', db.engine, index_col='index')
    Y = np.array(rateallclimbs(featdict, samplesdf, featdf,
                               features))  # use user input to predict ratings for each of these candidates (based on reduced space)
    X = Xdf.loc[Xdf['climbid'].isin(candidateids), allfeatures].values
    clf.fit(X, Y)  # use predicted ratings as "labels" to train a full model
    finalclf = savefinalmodel(X, Y, clf, userid, allfeatures, featdict, os.path.join(fulldir, 'data'))
    addnewuserstars(db, userid, username, candidateids, Y)
    return finalclf


def savefinalmodel(X, Y, clf, u, features, featdict, datadir):
    '''save that user's model'''
    clf.fit(X, Y)
    finalclf = {'user': u, 'clf': clf, 'finalfeats': features}
    fname = 'models/user_%s_model.pkl' % (int(u))
    filename = os.path.join(datadir, fname)
    with open(filename, 'wb') as output:
        pickler = pickle.Pickler(output, pickle.HIGHEST_PROTOCOL)
        try:
            pickler.dump(finalclf)
        except:
            warnings.warn("pickle fail")
    current_app.modeldicts['user_%s_model.pkl' % int(u)] = finalclf
    current_app.featdicts['feats_%s' % int(u)] = featdict
    print "added user_%s_model.pkl" % int(u)
    return finalclf


def getscore(featdf, f, val):
    '''get score that this value is associated with for this feature f'''
    rowvals = list(featdf[featdf['feature'] == f][[1, 2, 3, 4]].values[0])
    return rowvals.index(val) + 1


def rateclimb(featweights, row):
    '''compute users rating of the climb given their expressed preferences and the climb's features'''
    ratings = np.multiply(featweights, row)
    return np.mean(ratings)


def getstar(value, one=0, two=0, three=0):
    if value < one: return 1
    elif value < two: return 2
    elif value < three: return 3
    else: return 4


def rateallclimbs(userdict, samplesdf, featdf, reducedfeats):
    '''get climber's ratings on all climbs in sample set'''
    featweights = [
        float(userdict[current_app.askfeatures_dict[feat]]) - 2 if feat[:feat.index('_')] in userdict.keys() else 0 for
        feat in current_app.askfeatures]
    featweights.insert(reducedfeats.index('avgstars'), .1)
    samplesdf['score'] = samplesdf.apply(lambda x: rateclimb(featweights, x[reducedfeats].values), axis=1)
    arr = samplesdf['score'].values
    quarter = np.percentile(arr, 25)
    half = np.percentile(arr, 50)
    threequarters = np.percentile(arr, 75)
    orderedsamples = samplesdf['score'].apply(getstar, one=quarter, two=half, three=threequarters)
    return orderedsamples

