# generates page of climb info
from ormcfg import ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable
from sqlalchemy import func
import pagedata.user as uf
import pagedata.climb as cf
import pagedata.area as af
import pagedata.home as hf
import pandas as pd

from config import rootdir

################     HOME PAGE    ####################

'''
def initial_home(g):
    avail=hf.getall(g)
    return hf.gettopclimbs(g.db), avail
'''
def initial_home(g):
    return hf.gettopclimbs(g.db)
'''
def result_home_meh(request, g):
    print "AAAA"
    print request.form['name']
    name=request.form['name']
    result=hf.matchname(name, g)
    print result
    return result
'''
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
    urecs=uf.getuserrecs(udict, g.db, areaid, gradeshift, sport, trad, boulder)
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
    climbid=int(inputdict['climbid'])
    c=g.db.session.query(ClimbTable).filter_by(climbid=climbid).first()
    cdict=cf.getclimbdict(c, g.db, getnest=True)
    del cdict['_sa_instance_state']
    crecs=cf.getsimilarclimbs(g.db, climbid, ClimbTable)
    return cdict, crecs