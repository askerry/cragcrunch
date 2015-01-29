# generates page of climb info
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
from sqlalchemy import func
import pagedata.user as uf
import pagedata.newuser as nuf
import pagedata.climb as cf
import pagedata.area as af
import pagedata.home as hf
import pandas as pd
import timeit

from config import rootdir

################     HOME PAGE    ####################

def initial_home(g):
    climbs=hf.gettopclimbs(g.db)
    users=hf.getusers(g.db)
    t=timeit.default_timer()
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
    if areaid is None:
        areaid=udict['mainarea']
    #urecs={}
    urecs=uf.getuserrecs(udict, g.db, areaid, gradeshift, sport, trad, boulder) #time suck
    uplotdata=uf.getuserplots(udict, g.db)
    areas=uf.getmainareaoptions(g.db)
    return udict, urecs, uplotdata, areas, udict['mainarea']

################     AREA PAGE    ####################


def getareapage(g, inputdict):
    areaid=inputdict['areaid']
    a=g.db.session.query(AreaTable).filter_by(areaid=areaid).first()
    adict=af.getareadict(a, g.db)
    del adict['_sa_instance_state']
    aplotdata=af.getplotdata(adict['allchildren'], g.db)
    return adict, aplotdata
    

################     CLIMB PAGE    ####################


def getclimbpage(g, inputdict):
    climbid=int(float(inputdict['climbid']))
    c=g.db.session.query(ClimbTable).filter_by(climbid=climbid).first()
    cdict=cf.getclimbdict(c, g.db, getnest=True)
    crecs=cf.getsimilarclimbs(g.db, climbid, ClimbTable)
    del cdict['_sa_instance_state']
    return cdict, crecs

##############     NEW USER PAGE    ##################

def getnewuseroptions(g):
    states=nuf.getstates(g.db)
    areas=uf.getmainareaoptions(g.db)
    bouldergrades=nuf.getbouldergrades()
    routegrades=nuf.getroutegrades()
    return states, areas, bouldergrades, routegrades

def adduser(g, request):
    udict=nuf.addtodb(g.db, request)
    return udict