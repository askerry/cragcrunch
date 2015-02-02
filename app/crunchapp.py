import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify, current_app, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ormcfg import ClimberTable
from sqlalchemy.sql import text
import pages as pinf
import pagedata.user as uf
import pagedata.newuser as nuf
import sys
import pickle
import os
import timeit
import config
from config import fulldir
sys.path.append(fulldir)
import antools.randomstuff as rd
from collections import OrderedDict
import pandas as pd

# create application
app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


class DBConnection():
    def __init__(self, engine):
        Session = sessionmaker(bind=engine) # create a configured "Session" class
        self.session = Session() # create a Session
        self.engine=engine
    def close(self):
        self.session.close()
    def rawsql(self, string):
        sql=text(string)
        returned = self.engine.execute(sql)
        entries=[]
        for row in returned:
            entries.append(dict(title=row[0], text=row[1]))
        return entries


def connect_db():
    #create engine that Session will use for connection
    cfg=app.config['DBCFG']
    engine = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' %(cfg.user, cfg.host, cfg.dbname, cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)
    return DBConnection(engine)

def check_db_connection():
    dbconn=connect_db()
    return dbconn

#testconn=check_db_connection()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#views

@app.route('/')
@app.route('/<status>')
def land(status=""):
    if status=='invalid':
        helper="Oops. Your username & password were invalid. Please sign in again or continue as Guest."
    else:
        helper=''
    return render_template('landing.html', helper=helper)

@app.route('/home', methods=['POST'])
def home():
    username=request.form['username']
    matches=g.db.session.query(ClimberTable).filter(ClimberTable.name.ilike(username)).all()
    if request.form['guest']=='guest':
        current_app.userid=2424
        current_app.username=g.db.session.query(ClimberTable).filter_by(climberid=current_app.userid).all()[0].name
    else:
        if len(matches)==0:
            return redirect('/invalid')
        else:
            current_app.userid=matches[0].climberid
            current_app.username=matches[0].name
    climbs,users=pinf.initial_home(g)
    return render_template('home.html', returntype='noresult', climbs=climbs, users=users, loggedinid=current_app.userid, loggedinname=current_app.username)

@app.route('/result', methods=['POST'])
def search():
    result=pinf.result_home(request, g)
    return render_template('home.html', returntype='result', result=result, loggedinid=current_app.userid, loggedinname=current_app.username)


@app.route('/view')
@app.route('/view/<searchid>')
def view(searchid=0):
    if 'climb' in searchid:
        climbid=searchid[5:]
        cdict, crecs=pinf.getclimbpage(g, {'climbid':climbid})
        return render_template('climbview.html', climb=cdict, recs=crecs, loggedinid=current_app.userid, loggedinname=current_app.username)
    if 'area' in searchid:
        areaid=searchid[4:]
        adict, aplotdata=pinf.getareapage(g, {'areaid':areaid})
        return render_template('areaview.html', area=adict, plotdata=aplotdata, loggedinid=current_app.userid, loggedinname=current_app.username)
    else:
        return render_template('pagenotfound')

@app.route('/user')
@app.route('/user/<userid>')
def user(userid=123):
    userdict, userrecs, userplotdata, areas, defaultarea=pinf.getuserpage(g, {'userid':userid})
    return render_template('user.html', user=userdict, recs=userrecs, plotdata=userplotdata, areas=areas, defaultarea=float(defaultarea), loggedinid=current_app.userid, loggedinname=current_app.username)

@app.route('/about')
def about():
    text='test text test text'
    return render_template('about.html', text=text, loggedinid=current_app.userid, loggedinname=current_app.username)

@app.route("/refreshrecs", methods=['GET', 'POST'])
def updaterecs():
    areaid=request.args.get('areaid')
    userid=request.args.get('userid')
    gs=request.args.get('gradeshift')
    #this seems janky?
    js2bool={'true':True, 'false':False}
    sport=js2bool[request.args.get('sportcheck')]
    trad=js2bool[request.args.get('tradcheck')]
    boulder=js2bool[request.args.get('bouldercheck')]
    print sport, trad, boulder
    udict, urecs, uplotdata, areas, udict['mainarea']=pinf.getuserpage(g, {'userid':userid}, areaid=areaid, gradeshift=gs, sport=sport, trad=trad, boulder=boulder)
    return jsonify({'recs':urecs})

@app.route("/newuser/<username>", methods=['GET', 'POST'])
def newuser(username):
    states, areas, bouldergrades, routegrades=pinf.getnewuseroptions(g)
    return render_template('newuser.html', username=username, states=states, areas=areas, bouldergrades=bouldergrades, routegrades=routegrades, loggedinid=current_app.userid, loggedinname=current_app.username)

@app.route("/newuser/preferences", methods=['GET', 'POST'])
def newuserpred():
    udict=pinf.adduser(g, request)
    features=[f for f in current_app.askfeatures_terms if f not in rd.blockterms]
    features={f:rd.labeldict[f] if f in rd.labeldict.keys() else f for f in features}
    return render_template('newuserprefs.html', udict=udict, redfeats=features, loggedinid=current_app.userid, loggedinname=current_app.username)

@app.route("/newuser/createprofile", methods=['GET', 'POST'])
def createuserprofile():
    print "xxxx"
    print request.form
    userid,featdict=pinf.getuserinput(request, current_app.askfeatures)
    clf=nuf.modelnewuser(g.db, featdict, userid)
    app.modeldicts[filename]=clf
    userdict, userrecs, userplotdata, areas, defaultarea=pinf.getuserpage(g, {'userid':userid})
    return render_template('user.html', user=userdict, recs=userrecs, plotdata=userplotdata, areas=areas, defaultarea=float(defaultarea),loggedinid=current_app.userid, loggedinname=current_app.username)


@app.route("/checkavailability", methods=["GET"])
def checkavailability():
    desiredname=request.args.get('desiredname')
    matches=g.db.session.query(ClimberTable).filter_by(name=desiredname).all()
    if len(matches)==0:
        return jsonify({'exists':False, 'name':desiredname})
    else:
        return jsonify({'exists':True, 'name':desiredname})


if __name__ == '__main__':
    modeldir=os.path.join(fulldir, 'data/models')
    modelfiles=os.listdir(modeldir)
    app.modeldicts={}
    for filename in modelfiles:
        try:
            with open(os.path.join(modeldir, filename), 'r') as inputfile:
                model=pickle.load(inputfile)
        except:
            model=[]
        app.modeldicts[filename]=model
    app.userid=2424
    app.username='GhaMby'
    with open(config.redfeatfile, 'r') as inputfile:
        d=pickle.load(inputfile)
        app.askfeatures=d['reducedtextfeats']
        app.askfeatures_terms=list(set([t[:t.index('_')] for t in app.askfeatures if '_' in t]))
        featdict={}
        for f in app.askfeatures:
            if '_' in f:
                featdict[f]=f[:f.index('_')]
            else:
                featdict[f]=f
        app.askfeatures_dict=featdict
    app.run(debug=True, host='0.0.0.0')
