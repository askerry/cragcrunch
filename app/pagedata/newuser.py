__author__ = 'amyskerry'

from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
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
import sys
from collections import OrderedDict
import pickle
import pdb

rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
dirname=os.path.join(rootdir, 'Projects', 'cragcrunch/')
sys.path.append(dirname)
import antools
from config import rootdir, projectroot,clf
import antools.randomstuff as rd

def getstates(db):
    states=db.session.query(AreaTable).filter_by(region='World').all()
    states={state.name:state.areaid for state in states if state.name!='* In Progress'}
    alphastates=sorted(states.keys())
    return OrderedDict((states[key],key) for key in alphastates if key !='* In Progress')

def getbouldergrades():
    return rd.listgrades_boulder

def getroutegrades():
    return rd.listgrades_route

def addtodb(db, request):
    styles=[]
    if request.form['sportcheck']=='Sport':
        styles.append('Sport')
    if request.form['tradcheck']=='Trad':
        styles.append('Trad')
    if request.form['bouldercheck']=='Boulder':
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
    print maxclimberid
    nuser.climberid=maxclimberid+1
    db.session.add(nuser)
    db.session.flush()
    print nuser.climberid
    print nuser.id
    print "???"
    ndict['climberid']=float(nuser.climberid)
    db.session.commit()
    del ndict['_sa_instance_state']
    print ndict
    return ndict

def modelnewuser(db, userdf):
    newuserfeats=rd.reducedfeats
    samplesdf=pd.read_sql('select * from fakesamples', db.engine)
    featdf=pd.read_sql('select * from fakesamples', db.engine)
    Y=np.array(rateallclimbs(userdf, samplesdf, featdf, newuserfeats))
    X=samplesdf.values
    clf.fit(X,Y)
    finalclf=savefinalmodel(X,Y,clf,userdf['user'].values[0],newuserfeats,os.path.join(rootdir, projectroot, 'data'))
    return clf

def savefinalmodel(X,Y,clf,u,features,datadir):
    clf.fit(X, Y)
    finalclf={'user':u, 'clf':clf, 'features':features}
    fname='models/user_%s_model.pkl'%(u)
    filename=os.path.join(datadir,fname)
    with open(filename, 'wb') as output:
        pickler = pickle.Pickler(output, pickle.HIGHEST_PROTOCOL)
        try:
            pickler.dump(finalclf)
        except:
            print "pickle fail"
    return finalclf

def getscore(featdf,f,val):
    '''get score that this value is associated with for this feature f'''
    rowvals=list(featdf[featdf['feature']==f][[1,2,3,4]].values[0])
    return rowvals.index(val)+1

def rateclimb(userdf, sampledf, featdf, reducedfeats):
    '''compute users rating of the climb given their expressed preferences and the climb's features'''
    ratings=[]
    for f in reducedfeats:
        value=sampledf[f]
        fscore=getscore(featdf,f,value)
        userscore=userdf[userdf['feature']==f]['pref'].values[0]
        ratings.append(4-np.abs(fscore-userscore))
    return np.mean(ratings)


def rateallclimbs(userdf, samplesdf, featdf, reducedfeats):
    '''get climber's ratings on all climbs in sample set'''
    ratings=samplesdf.apply(lambda x:rateclimb(userdf, x[:], featdf, reducedfeats), axis=1)
    return ratings