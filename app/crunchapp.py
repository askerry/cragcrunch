import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import pages as pinf


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
    print "opened connection"

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    print "closed connection"


#views

@app.route('/home')
@app.route('/')
def home():
    #result, avail=pinf.initial_home(g)
    result=pinf.initial_home(g)
    #return render_template('home.html', returntype='noresult', result=result, avail=avail)
    return render_template('home.html', returntype='noresult', result=result)

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
    changetype=request.args.get('changetype')
    print changetype
    userid=request.args.get('userid')
    print userid
    areaid=request.args.get('areaid')
    print areaid
    if changetype=='areachange':
        areaid=request.args.get('areaid')
        userid=request.args.get('userid')
        udict, urecs, uplotdata, areas, udict['mainarea']=pinf.getuserpage(g, {'userid':userid}, areaid=areaid)
    print "SADGASGD"
    return jsonify({'recs':urecs})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
