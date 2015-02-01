__author__ = 'amyskerry'

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
from flask import current_app
import numpy as np
import pandas as pd
import viz
import misc
import json
from flask import jsonify
import home as hf
import climb as cf
import os
from sqlalchemy import and_
from sqlalchemy.sql import func
import user as uf
import sys
from collections import OrderedDict
import pickle
import pdb
from config import fulldir,clf
sys.path.append(fulldir)
import antools.randomstuff as rd
import config

def getstates(db):
    '''get ordered dict of all possible states'''
    states=db.session.query(AreaTable).filter_by(region='World').all()
    states={state.name:state.areaid for state in states if state.name!='* In Progress'}
    alphastates=sorted(states.keys())
    return OrderedDict((states[key],key) for key in alphastates if key !='* In Progress')

def getbouldergrades():
    return rd.listgrades_boulder

def getroutegrades():
    return rd.listgrades_route

def addtodb(db, request):
    '''take basic user info and save user to be'''
    styles=[]
    if request.form['sportcheckhidden']=='true':
        styles.append('Sport')
    if request.form['tradcheckhidden']=='true':
        styles.append('Trad')
    if request.form['bouldercheckhidden']=='true':
        styles.append('Boulder')

    styles=', '.join(styles)
    name=request.form['name']
    if request.form['mainarea']=='Empty':
        mainarea=0
    else:
        mainarea=float(request.form['mainarea'])
    nuser=ClimberTable(name=str(request.form['name']), gender=str(request.form['gender']), climbstyles=styles, region=float(request.form['state']), mainarea=mainarea)
    if request.form['sportgrade'] == 'Empty':
        nuser.g_median_Sport=39.0
    else:
        nuser.g_median_Trad = float(request.form['tradgrade'])
    if request.form['tradgrade'] == 'Empty':
        nuser.g_median_Trad=28.0
    else:
        nuser.g_median_Sport = float(request.form['sportgrade'])
    if request.form['bouldergrade'] == 'Empty':
        nuser.g_median_Boulder=14.0
    else:
        nuser.g_median_Boulder = float(request.form['bouldergrade'])
    ndict={item[0]:item[1] for item in nuser.__dict__.items()}
    maxclimberid=float(db.session.query(func.max(ClimberTable.climberid)).first()[0])
    nuser.climberid=maxclimberid+1
    db.session.add(nuser)
    db.session.flush()
    ndict['climberid']=float(nuser.climberid)
    db.session.commit()
    del ndict['_sa_instance_state']
    return ndict

def modelnewuser(db, userdict, userid):
    '''take a dataframe of user expressed preferences and build a model of them'''
    with open(config.redfeatfile, 'r') as inputfile:
        newuserfeats=pickle.load(inputfile)['reducedtextfeats']
    candidateids=uf.getcandidates(userdict, db, userdict['mainarea'], 0, userdict['styles'])
    samplesdf=pd.read_sql('select * climb_prepped here climbid in (%s)' %','.join(candidateids), db.engine, index_col='index')
    featdf=pd.read_sql('select * from featranges', db.engine, index_col='index')
    Y=np.array(rateallclimbs(userdict, samplesdf, featdf, newuserfeats))
    X=samplesdf.values
    clf.fit(X,Y)
    finalclf=savefinalmodel(X,Y,clf,userid,newuserfeats,os.path.join(fulldir, 'data'))
    return finalclf

def modelnewuser_old(db, userdict, userid):
    '''take a dataframe of user expressed preferences and build a model of them'''
    with open(config.redfeatfile, 'r') as inputfile:
        newuserfeats=pickle.load(inputfile)['reducedtextfeats']
    samplesdf=pd.read_sql('select * from fakesamples', db.engine, index_col='index')
    samplesdf=samplesdf[newuserfeats]
    samplesdf=(samplesdf - samplesdf.mean()) / (samplesdf.std())
    featdf=pd.read_sql('select * from featranges', db.engine, index_col='index')
    Y=np.array(rateallclimbs(userdict, samplesdf, featdf, newuserfeats))
    X=samplesdf.values
    clf.fit(X,Y)
    finalclf=savefinalmodel(X,Y,clf,userid,newuserfeats,os.path.join(fulldir, 'data'))
    return finalclf

def savefinalmodel(X,Y,clf,u,features,datadir):
    '''save that user's model'''
    clf.fit(X, Y)
    finalclf={'user':u, 'clf':clf, 'finalfeats':features}
    fname='models/newuser_%s_model.pkl'%(u)
    filename=os.path.join(datadir,fname)
    with open(filename, 'wb') as output:
        pickler = pickle.Pickler(output, pickle.HIGHEST_PROTOCOL)
        try:
            pickler.dump(finalclf)
        except:
            print "pickle fail"
    current_app.modeldicts['newuser_%s_model.pkl'%int(u)]=finalclf
    print "added newuser_%s_model.pkl" %int(u)
    return finalclf

def getscore(featdf,f,val):
    '''get score that this value is associated with for this feature f'''
    rowvals=list(featdf[featdf['feature']==f][[1,2,3,4]].values[0])
    return rowvals.index(val)+1

def rateclimb_old(userdict, sampledf, featdf, reducedfeats, samplesdf):
    '''compute users rating of the climb given their expressed preferences and the climb's features'''
    ratings=[]
    for f in reducedfeats:
        value=sampledf[f]
        fscore=getscore(featdf,f,value)
        try:
            userscore=userdict[f]
        except:
            userscore=2.5
        ratings.append(4-np.abs(fscore-userscore))
    return round(np.mean(ratings))


def rateclimb(featweights, row):
    '''compute users rating of the climb given their expressed preferences and the climb's features'''
    print featweights
    print row
    ratings=np.multiply(featweights, row)
    print ratings
    return np.mean(ratings)

def getstar(value, quantile=0):
    if value<quantile:
        return 1
    elif value<quantile*2:
        return 2
    elif value<quantile*3:
        return 3
    elif value<=quantile*4:
        return 4

def rateallclimbs(userdict, samplesdf, featdf, reducedfeats):
    '''get climber's ratings on all climbs in sample set'''
    featdict={}
    for f in reducedfeats:
        if '_' in f:
            featdict[f]=f[:f.index('_')]
        else:
            featdict[f]=f
    featdf.index=featdf.feature.values
    featweights=[float(userdict[featdict[feat]]) if feat in userdict.keys() else 0 for feat in reducedfeats]
    samplesdf['score']=samplesdf.apply(lambda x:rateclimb(featweights, x[:].values), axis=1)
    quarter=samplesdf['score'].quantile(.25)
    orderedsamples=samplesdf['score'].apply(getstar, quantile=quarter)
    return orderedsamples

