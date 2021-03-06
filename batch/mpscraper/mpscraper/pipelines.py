# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting...see: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from mpscraper.items import Climb, Area, Climber, Ticks, Comments, Stars, Grades, ToDos
from cfgdb import cfg, ClimbTable, AreaTable, ClimberTable, TicksTable, CommentsTable, StarsTable, GradesTable, ToDosTable
#import MySQLdb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dateutil.parser
import warnings
import datetime
import os

dbdict={'climb':ClimbTable, 'area':AreaTable, 'mainarea':AreaTable,'climber':ClimberTable}
mapping={Climb:ClimbTable, Area:AreaTable, Climber:ClimberTable, Ticks:TicksTable, Comments:CommentsTable, Stars:StarsTable, Grades:GradesTable, ToDos:ToDosTable}

# pipeline functions

def logfail(item, o):
    rootdir='/home/amyskerry/Projects/climbrec/mpscraper/log'
    with open(os.path.join(rootdir, "errorlog.txt"), "a") as log:
        itemtype=item.__class__.__name__
        url=item['url']
        try:
            oname=o['name']
        except:
            oname=''
        log.write("%s: %s (%s) failed .... %s" % (datetime.datetime.now(), itemtype, url, oname))

def addandgetid(newobj, dbconn):
    '''adds an object and gets its primary ID'''
    dbconn.session.add(newobj)
    dbconn.session.commit()
    field=[f for f in dir(newobj) if 'id' in f][0]
    fid=getattr(newobj, field)
    return fid
    
def findorcreate(item, f, foreignclass, dbconn, extrafield=None):
    '''takes a field (or pair of fields) and finds a match or creates a new object. returns new or existing primary id'''
    name=item[f]
    if extrafield:
        url=item[extrafield]
        rows=dbconn.session.query(foreignclass).filter(foreignclass.name == name, foreignclass.url == url)
    else:
        rows=dbconn.session.query(foreignclass).filter(foreignclass.name == name)
    try:
        returned=[r for r in rows]
        field=[f for f in dir(returned[0]) if 'id' in f and 'aid_' not in f][0]
        pid=getattr(returned[0], field)
    except:
        nrow=foreignclass()
        nrow.name=name
        if extrafield:
            nrow.url=url
        pid=addandgetid(nrow, dbconn)
    return pid

def findforeignkey(f,item, dbconn):
    '''takes name looks up primary key associated with that name in the relevant table (if area, looks for both area name and area main area). returns primary key of match.'''
    value=item[f]
    foreignclass=dbdict[f]
    if f=='area': #if we are looking up the key for an area, we want to be sure it has the same name and the same higher-level area (to deal with possible repeats)
        value=findorcreate(item,f, foreignclass, dbconn, extrafield='areaurl')
    elif f=='climb':
        value=findorcreate(item,f, foreignclass, dbconn, extrafield='climblink')
    else:
        value=findorcreate(item,f, foreignclass, dbconn)
    return value

def checkname(obj, tabletype, dbconn):
    '''checks whether a item with this name (and url if relevant) is already in the database. adds relevant primary id to object if it is'''
    if 'areaid' in dir(obj) or 'climbid' in dir(obj): #gets us climbs and areas
        rows=dbconn.session.query(tabletype).filter(tabletype.name == obj.name, tabletype.url == obj.url)
    else:
        rows=dbconn.session.query(tabletype).filter(tabletype.name == obj.name)
    returned=[r for r in rows]
    if len(returned)>0:
        field=[f for f in dir(obj) if 'id' in f][0]
        pkey=getattr(returned[0], field)
        setattr(obj, field, pkey)
    return obj

def convertunicode(itemfields,obj):
    for f in itemfields:
        r=getattr(obj,f)
        try:
            setattr(obj, f, r.encode('utf8'))
        except:
            pass
        return obj
    
def write2db(item, tabletype, dbconn):
    '''translates item to sqlalchemy class and writes to database. determines primary key for updating, and looks up appropriate foreign keys'''
    obj=tabletype()
    fields=item.fields.keys()
    for f in fields:
        if f not in ['areaurl']:
            try:
                value=item[f]
                if f in dbdict.keys(): #if this is a foreign key field, find the relevant keys
                    value=findforeignkey(f,item, dbconn)
                if type(value)==str:
                    value=value.strip()
                setattr(obj, f, value)
            except:
                pass
    try:
        obj=checkname(obj, tabletype, dbconn)
        print obj
        dbconn.session.merge(obj) #merges with existing or adds if no primary key match
        dbconn.session.commit()
        print "success!"
    except:
        try:
            obj=convertunicode(fields,obj)
            obj=checkname(obj, tabletype, dbconn)
            dbconn.session.merge(obj) #merges with existing or adds if no primary key match
            dbconn.session.commit()
            print "success"
        except:
            dbconn.session.rollback()
            print "DB SAVE FAILED"
            raise
    finally:
        dbconn.session.close()

def overwritecheck(dbconn, tablename, item):
    '''checks whether clobber is True. if not, returns write boolean as true only if the url is not in the database. if clobbering, returns true regardless of existing entries.'''
    if cfg.clobber:
        warnings.warn('clobber is set to True. we will overwrite entries.')
        write=True
    else:
        foreignclass=mapping[type(item)]
        url=item['url']
        if tablename.lower() in ['area','climb']:
            region=item['region']
            rows=dbconn.session.query(foreignclass).filter(foreignclass.url == url, foreignclass.region == region) #urls get added even without full entries, so for area and climb we'll look for a region value to determine if we want to fill this in
        elif tablename.lower() in ['ticks', 'todos', 'stars', 'grades', 'comments']:
            name=item['name']
            rows=dbconn.session.query(foreignclass).filter(foreignclass.url == url, foreignclass.name == name) #multiple entries come from the same url, so we'll fill this in only if the name and url match
        else:
            rows=dbconn.session.query(foreignclass).filter(foreignclass.url == url)
        returned=[r for r in rows]
        if len(returned)==0:
            write=True
        else:
            write=False
    return write

'''    
class DBConnectionRaw():
    #could use if we want to write raw sql commands at anypoint
    def __init__(self):
        self.conn = MySQLdb.connect(user=cfg.user, passwd=cfg.passwd, db=cfg.dbname, host=cfg.host, charset=cfg.charset, use_unicode=cfg.charset)
        self.cursor = self.conn.cursor()
'''
      
class DBConnection():
    def __init__(self):
        #create engine that Session will use for connection
        some_engine = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' %(cfg.user, cfg.host, cfg.dbname, cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)
        Session = sessionmaker(bind=some_engine) # create a configured "Session" class  
        self.session = Session() # create a Session
        
#specialized pipeline functions for each type of subentry

def makesingleticks(item, dbconn):
    if len(item['climb'])==len(item['climblink'])==len(item['note'])==len(item['date']):
        for tickn,tick in enumerate(item['climb']):
            try:
                t=Ticks()
                t['note']=item['note'][tickn]
                t['date']=dateutil.parser.parse(item['date'][tickn])
                t['climblink']=item['climblink'][tickn]
                t['climber']=item['climber']
                t['url']=item['url']
                t['name']=item['name']='%s_%s' %(item['climber'], tick)
                t['climb']=tick
                if overwritecheck(dbconn, item.__class__.__name__, t):
                    write2db(t, mapping[type(item)], dbconn)
                else:
                    warnings.warn('existing record. clobber==False so we will not overwrite')
            except:
                warnings.warn('item %s failed' %tick)
                logfail(item, t)
    else:
        warnings.warn("item %s failed. unqual lengths" %tick)
        logfail(item, t)
            
def makesingletodos(item, dbconn):
    if len(item['climb'])==len(item['climblink']):
        for todon,todo in enumerate(item['climb']):
            try:
                t=ToDos()
                t['climblink']=item['climblink'][todon]
                t['climber']=item['climber']
                t['url']=item['url']
                t['name']=item['name']='%s_%s' %(item['climber'], todo)
                t['climb']=todo
                if overwritecheck(dbconn, item.__class__.__name__, t):
                    write2db(t, mapping[type(item)], dbconn)
                else:
                    warnings.warn('existing record. clobber==False so we will not overwrite')
            except:
                warnings.warn('item %s failed' %todo)
                logfail(item, t)
    else:
        warnings.warn("item %s failed. unqual lengths" %todo)
        logfail(item, t)
       

def makesinglecomments(item, dbconn):
    if len(item['climb'])==len(item['climblink'])==len(item['comment'])==len(item['date']):
        for commentn,comment in enumerate(item['climb']):
            try:
                if comment != 'Photo':
                    try:
                        comment=comment[:-1][:-(comment[::-1].index('(')+1)] #removing the grade
                    except:
                        pass
                    c=Comments()
                    c['climblink']=item['climblink'][commentn]
                    c['climber']=item['climber']
                    try:
                        c['date']=dateutil.parser.parse(item['date'][commentn])
                    except:
                        pass
                    c['comment']=item['comment'][commentn]
                    if len(c['comment'])>7:
                        tag=c['comment'][:6]
                    else:
                        tag=c['comment']
                    c['url']=item['url']
                    c['name']=item['name']='%s_%s_%s...' %(item['climber'], comment, tag)
                    c['climb']=comment
                    if overwritecheck(dbconn, item.__class__.__name__, c):
                        write2db(c, mapping[type(item)], dbconn)
            except:
                warnings.warn('item %s failed' %comment)
                logfail(item, c)
    else:
        warnings.warn("item %s failed. unqual lengths" %comment)
        logfail(item, t)
        
def makesinglestars(item, dbconn):
    if len(item['climb'])==len(item['climblink'])==len(item['starsscore']):
        for starn,star in enumerate(item['climb']):
            try:
                s=Stars()
                s['climblink']=item['climblink'][starn]
                s['climber']=item['climber']
                s['starsscore']=item['starsscore'][starn]
                s['url']=item['url']
                s['name']=item['name']='%s_%s' %(item['climber'], star)
                s['climb']=star
                if overwritecheck(dbconn, item.__class__.__name__, s):
                    write2db(s, mapping[type(item)], dbconn)
            except:
                warnings.warn('item %s failed' %star)
                logfail(item, s)
    else:
        warnings.warn("item %s failed. unqual lengths" %star)
        logfail(item, t)

def makesinglegrades(item, dbconn):
    if len(item['climb'])==len(item['climblink'])==len(item['grade']):
        for graden,grade in enumerate(item['climb']):
            try:
                g=Grades()
                g['climblink']=item['climblink'][graden]
                g['climber']=item['climber']
                g['grade']=item['grade'][graden]
                g['url']=item['url']
                g['name']=item['name']='%s_%s' %(item['climber'], grade)
                g['climb']=grade
                if overwritecheck(dbconn, item.__class__.__name__, g):
                    write2db(g, mapping[type(item)], dbconn)
            except:
                warnings.warn('item %s failed' %grade)
                logfail(item, g)
    else:
        warnings.warn("item %s failed. unqual lengths" %grade)
        logfail(item, t)
        
class DBPipeline(object):
    def add2db(self):
        try:
            dbconn=DBConnection()
            if self.tablename=='Ticks':
                makesingleticks(self.item, dbconn)
            elif self.tablename=='ToDos':
                makesingletodos(self.item, dbconn)
            elif self.tablename=='Comments':
                makesinglecomments(self.item, dbconn)
            elif self.tablename=='Stars':
                makesinglestars(self.item, dbconn)
            elif self.tablename=='Grades':
                makesinglegrades(self.item, dbconn)
            else:
                if overwritecheck(dbconn, self.tablename, self.item):
                    write2db(self.item, self.tabletype, dbconn)
                else:
                    warnings.warn('existing record. clobber==False so we will not overwrite')
        except:
            print "DB PIPELINE FAILED"
            warnings.warn('DB PIPELINE FAILED')
            print self.item
            print "******************************************"
    def process_item(self, item, spider):
        self.item=item
        self.tabletype=mapping[type(item)]
        self.tablename=item.__class__.__name__
        self.add2db()
        return item
    
