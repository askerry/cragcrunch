# generates page of climb info
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
from flask import current_app, session
from sqlalchemy import func
import pagedata.user as uf
import pagedata.newuser as nuf
import pagedata.climb as cf
import pagedata.area as af
import config
import os
import warnings
import pickle
import pagedata.home as hf
import pandas as pd
import timeit
from config import fulldir,clf
import sys
sys.path.append(fulldir)
import antools.randomstuff as rd


from config import fulldir

################     HOME PAGE    ####################

def initial_home(g):
    climbs=hf.gettopclimbs(g.db)
    users=hf.getusers(g.db)
    return climbs,users

def result_home(request, g):
    text = request.form['text']
    finds=hf.findmatch(text, g)
    return finds

################     USER PAGE    ####################


def getuserpage(g, inputdict, areaid=None, gradeshift=0, sport=True, trad=True, boulder=True):
    climberid=inputdict['userid']
    a=g.db.session.query(ClimberTable).filter_by(climberid=climberid).first()
    udict=uf.getuserdict(a, g.db)
    ###omg hack
    if climberid>8729:
        udict['newuser']=True
    else:
        udict['newuser']=False
    if areaid is None:
        areaid=udict['mainarea']
    try:
        urecs=uf.getuserrecs(udict, g.db, areaid, gradeshift, sport, trad, boulder) #time suck
    except:
        warnings.warn("failed to generate user recs")
        urecs=[]
    uplotdata=uf.getuserplots(udict, g.db)
    areas=uf.getmainareaoptions(g.db)
    return udict, urecs, uplotdata, areas, udict['mainarea']

################     AREA PAGE    ####################


def getareapage(g, inputdict):
    areaid=inputdict['areaid']
    a=g.db.session.query(AreaTable).filter_by(areaid=areaid).first()
    adict=af.getareadict(a, g.db)
    del adict['_sa_instance_state']
    #aplotdata=af.getplotdata(adict['allchildren'], g.db)
    aplotdata={}
    return adict, aplotdata
    

################     CLIMB PAGE    ####################


def getclimbpage(g, inputdict, userid):
    climbid=int(float(inputdict['climbid']))
    stars=cf.checkstars(g.db, climbid, userid)
    c=g.db.session.query(ClimbTable).filter_by(climbid=climbid).first()
    cdict=cf.getclimbdict(c, g.db, getnest=True)
    crecs=cf.getsimilarclimbs(g.db, climbid, ClimbTable)
    del cdict['_sa_instance_state']
    cdict['existingrating']=str(stars)
    return cdict, crecs

##############     NEW USER PAGE    ##################

def getuserinput(request, features):
    features=[f for f in current_app.askfeatures_terms if f not in rd.blockterms]
    userid=float(request.form['userid'])
    featdict={}
    for feat in features:
        featdict[feat]=request.form['pref_%s' %feat]
    #goof hack
    featdict['cracks']=featdict['crack']
    featdict['flake']=featdict['flakes']
    current_app.modeldicts['feats_%s' %int(userid)]=featdict
    return userid, featdict

def getnewuseroptions(g):
    states=nuf.getstates(g.db)
    areas=uf.getmainareaoptions(g.db)
    bouldergrades=nuf.getbouldergrades()
    routegrades=nuf.getroutegrades()
    return states, areas, bouldergrades, routegrades

def adduser(g, request):
    udict=nuf.addtodb(g.db, request)
    print 4
    udict['newuser']=True
    try:
        session['stash'][udict['climberid']]=udict
    except:
        session['stash']={udict['climberid']:udict}
    return udict