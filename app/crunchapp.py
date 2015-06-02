import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify, current_app, redirect
from ormcfg import ClimberTable, ProfileTable
import pages as pinf
import pagedata.user as uf
import pagedata.newuser as nuf
import warnings
import sys
import pickle
import json
import collections
import os
import timeit
import config
from config import fulldir
from collections import OrderedDict
import pandas as pd
import numpy as np
sys.path.append(fulldir)
from cfg.database_cfg import connect_db
import utilities.randomdata as rd

global default
default = 44946


# create application
app = Flask(__name__)
app.config.from_object('config')
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)
with open(os.path.join(app.config['ROOTDIR'], 'app/secret_key.txt')) as f:
    app.secret_key=f.read()

# slow data loading stuff

app.featdicts = {}
app.modeldicts = {}

app.config['FEATFILE']=os.path.join(app.config['ROOTDIR'], 'cfg/apriori.json')
app.config['ATTRIBUTEFILE']=os.path.join(app.config['ROOTDIR'], 'cfg/attributes.json')
with open(app.config['FEATFILE'], 'rb') as inputfile:
    app.features = json.loads(inputfile.read(), object_pairs_hook=collections.OrderedDict) 
with open(app.config['ATTRIBUTEFILE'], 'rb') as inputfile:
    app.attributes = json.loads(inputfile.read(), object_pairs_hook=collections.OrderedDict) 


@app.before_request
def before_request():
    g.db = connect_db(app)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

#views

@app.route('/')
@app.route('/<status>')
def land(status=""):
    if status == 'invalid':
        helper = "Oops. Your username is invalid. Please sign in again or continue as Guest."
    else:
        helper = ''
    return render_template('landing.html', helper=helper)

@app.route('/user/0')
def fallback():
    return render_template('landing.html', helper='')


@app.route('/home')
@app.route('/home', methods=['POST'])
def home():
    try:
        username = request.form['username']
        password = request.form['password']
        matches = g.db.session.query(ProfileTable).filter(ProfileTable.name.ilike(username)).all()
        if request.form['guest'] == 'guest':
            # default to Ben's Profile for guest user
            session['userid'] = default
            session['username'] = g.db.session.query(ClimberTable).filter_by(climberid=session['userid']).all()[0].name
        else:
            if len(matches) == 0:
                return redirect('/invalid')
            elif matches[0].password != password:
                return redirect('/invalid')
            else:
                session['userid'] = matches[0].userid
                session['username'] = matches[0].name
                session['password'] = password
    except:
        warnings.warn('session fail')
    climbs, users = pinf.initial_home(g)
    return render_template('home.html', returntype='noresult', climbs=climbs, users=users, loggedinid=session['userid'],
                           loggedinname=session['username'])


@app.route('/result', methods=['POST'])
def search():
    result = pinf.result_home(request, g)
    print result
    return render_template('home.html', returntype='result', result=result, loggedinid=session['userid'],
                           loggedinname=session['username'])




@app.route('/view')
@app.route('/view/<searchid>')
def view(searchid=0):
    if 'climb' in searchid:
        cdict, crecs = pinf.getclimbpage(g, {'climbid': searchid[5:]}, session['userid'])
        return render_template('climbview.html', climb=cdict, recs=crecs, loggedinid=session['userid'],
                               loggedinname=session['username'])
    if 'area' in searchid:
        adict, aplotdata = pinf.getareapage(g, {'areaid': searchid[4:]})
        return render_template('areaview.html', area=adict, plotdata=aplotdata, loggedinid=session['userid'],
                               loggedinname=session['username'])
    else:
        return render_template('pagenotfound')


@app.route('/user')
@app.route('/user/<userid>', methods=['GET'])
def user(userid=default):
    session['userid']=userid
    userdict, userrecs, userplotdata, areas, defaultarea = pinf.getuserpage(g, {'userid': userid})
    session['username']=userdict['name']
    return render_template('user.html', user=userdict, recs=userrecs, plotdata=userplotdata, areas=areas,
                           defaultarea=float(defaultarea), loggedinid=userid,
                           loggedinname=session['username'])
  

@app.route("/user/<userid>/preferences", methods=['GET', 'POST'])
def attributes(userid=default):
    attribute_dict=uf.load_preferences(g.db, userid, app.attributes)
    a_dict={}
    for key,value in app.attributes.items():
        a_dict[key]=value
        a_dict[key]['value']=attribute_dict[key]
    return render_template('attributes.html', userid=userid, a_dict=a_dict, loggedinid=session['userid'],
                           loggedinname=session['username'])


@app.route('/about')
def about():
    return render_template('about.html', loggedinid=session['userid'], loggedinname=session['username'])


@app.route("/updatepref", methods=['GET'])
def updatepref():
    userid = request.args.get('userid')
    feat = request.args.get('feat')
    value = float(request.args.get('value'))/24
    uf.updatepref(g.db, userid, feat, value)
    return redirect("/user/{}".format(userid))

@app.route("/refreshrecs", methods=['GET', 'POST'])
def updaterecs():
    areaid = request.args.get('areaid')
    userid = request.args.get('userid')
    grade = request.args.get('grade')
    #this is janky...
    js2bool = {'true': True, 'false': False}
    sport = js2bool[request.args.get('sportcheck')]
    trad = js2bool[request.args.get('tradcheck')]
    boulder = js2bool[request.args.get('bouldercheck')]
    udict, urecs, uplotdata, areas, udict['mainarea'] = pinf.getuserpage(g, {'userid': userid}, areaid=areaid,
                                                                         grade=grade, sport=sport, trad=trad,
                                                                         boulder=boulder)
    return jsonify({'recs': urecs})


@app.route("/checkavailability", methods=["GET"])
def checkavailability():
    desiredname = request.args.get('desiredname')
    matches = g.db.session.query(ClimberTable).filter_by(name=desiredname).all()
    existing = g.db.session.query(ProfileTable).filter_by(name=desiredname).all()
    if len(matches) > 0 and len(existing)==0:
        return jsonify({'reject': False, 'name': desiredname})
    else:
        return jsonify({'reject': True, 'name': desiredname})

@app.route("/user/import", methods=['GET', 'POST'])
def newuser():
    username = request.args.get('username')
    password = request.args.get('password')
    matches = g.db.session.query(ClimberTable).filter_by(name=username).all()
    userid=getattr(matches[0], 'climberid')
    session['username']=username
    session['password']=password
    session['userid']=userid
    uf.add_to_profile(g.db, matches[0], password)
    return redirect("/user/{}".format(userid))
    #redirect to user/<userid>

'''
@app.route("/newuser/<username>", methods=['GET', 'POST'])
def newuser(username):
    states, areas, bouldergrades, routegrades = pinf.getnewuseroptions(g)
    session['userid'] = 0
    session['username'] = username
    return render_template('newuser.html', username=username, states=states, areas=areas, bouldergrades=bouldergrades,
                           routegrades=routegrades, loggedinid=session['userid'], loggedinname=session['username'])


@app.route("/newuser/preferences", methods=['GET', 'POST'])
def newuserpred():
    udict = pinf.adduser(g, request)
    session['userid'] = udict['climberid']
    features = [f for f in current_app.askfeatures_terms if f not in rd.blockterms]
    features = {f: rd.labeldict[f] if f in rd.labeldict.keys() else f for f in features}
    return render_template('newuserprefs.html', udict=udict, redfeats=features, loggedinid=session['userid'],
                           loggedinname=session['username'])


@app.route("/newuser/createprofile", methods=['GET', 'POST'])
def createuserprofile():
    userid, username, featdict = pinf.getuserinput(request, current_app.askfeatures)
    userid=int(userid)
    clf = nuf.modelnewuser(g.db, featdict, userid, username)
    app.modeldicts[filename] = clf
    userdict, userrecs, userplotdata, areas, defaultarea = pinf.getuserpage(g, {'userid': userid})
    return render_template('user.html', user=userdict, recs=userrecs, plotdata=userplotdata, areas=areas,
                           defaultarea=float(defaultarea), loggedinid=session['userid'],
                           loggedinname=session['username'])


@app.route("/checkavailability", methods=["GET"])
def checkavailability():
    desiredname = request.args.get('desiredname')
    matches = g.db.session.query(ClimberTable).filter_by(name=desiredname).all()
    if len(matches) == 0:
        return jsonify({'exists': False, 'name': desiredname})
    else:
        return jsonify({'exists': True, 'name': desiredname})

@app.route("/logstar", methods=["POST"])
def logstar():
    rating = request.form['starsscore']
    climbid = request.form['climb']
    climbname = request.form['climbname']
    climbername = request.form['climbername']
    climberid = request.form['climber']
    uf.addstar(g.db, climberid, climbername, climbid, climbname, rating)
    print rating
    return jsonify({'returned': True, 'star':rating})
'''

@app.route("/blog")
def blog():
    return render_template('blog.html')

@app.route('/notebooks/<notebookname>')
def notebook(notebookname='Notebook1'):
    css='<link href="../static/bootstrap/css/bootstrap.min.css" rel="stylesheet"><link href="../static/bootstrap/css/bootstrap.css" rel="stylesheet"><link  href="../static/css/style.css" rel="stylesheet">'
    return render_template(notebookname+'.html', css=css)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
