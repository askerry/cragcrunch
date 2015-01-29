import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import pages as pinf
import pagedata.user as uf
import pickle
import os
import timeit
from config import fulldir
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

@app.route('/home')
@app.route('/')
def home():
    climbs,users=pinf.initial_home(g)
    return render_template('home.html', returntype='noresult', climbs=climbs, users=users)

@app.route('/home', methods=['POST'])
@app.route('/', methods=['POST'])
def search():
    result=pinf.result_home(request, g)
    return render_template('home.html', returntype='result', result=result)


@app.route('/view')
@app.route('/view/<searchid>')
def view(searchid=0):
    if 'climb' in searchid:
        climbid=searchid[5:]
        cdict, crecs=pinf.getclimbpage(g, {'climbid':climbid})
        return render_template('climbview.html', climb=cdict, recs=crecs)
    if 'area' in searchid:
        areaid=searchid[4:]
        adict, aplotdata=pinf.getareapage(g, {'areaid':areaid})
        return render_template('areaview.html', area=adict, plotdata=aplotdata)
    else:
        return render_template('pagenotfound')

@app.route('/user')
@app.route('/user/<userid>')
def user(userid=123):
    userdict, userrecs, userplotdata, areas, defaultarea=pinf.getuserpage(g, {'userid':userid})
    return render_template('user.html', user=userdict, recs=userrecs, plotdata=userplotdata, areas=areas, defaultarea=float(defaultarea))

@app.route('/about')
def about():
    text='test text test text'
    return render_template('about.html', text=text)

@app.route("/refreshrecs", methods=['GET', 'POST'])
def updaterecs():
    areaid=request.args.get('areaid')
    userid=request.args.get('userid')
    gs=request.args.get('gradeshift')
    print gs
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
    return render_template('newuser.html', username=username, states=states, areas=areas, bouldergrades=bouldergrades, routegrades=routegrades)

@app.route("/newuser/preferences", methods=['GET', 'POST'])
def newuserpred():
    udict=pinf.adduser(g, request)
    features=['crimp', 'boulder','flake']
    return render_template('newuserprefs.html', udict=udict, redfeats=features)

@app.route("/checkavailability", methods=["POST"])
def checkavailability():
    desiredname=request.args.get('desiredname')
    results=g.db.session
    matches=pd.read_sql("SELECT name from climber_prepped where name = '%s'" %desiredname, g.db.engine, index_col='index')['name'].unique()
    if len(matches)==0:
        return jsonify({'exists':False})
    else:
        return jsonify({'exists':True})


if __name__ == '__main__':
    modeldir=os.path.join(fulldir, 'data/models')
    modelfiles=os.listdir(modeldir)
    app.modeldict={}
    for filename in modelfiles:
        try:
            with open(os.path.join(modeldir, filename), 'r') as inputfile:
                model=pickle.load(inputfile)
        except:
            model=[]
        app.modeldict[filename]=model
    app.run(debug=True, host='0.0.0.0')
