# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 10:59:23 2014

@author: amyskerry

build database for climbing data

"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base

import sys, os
rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
sys.path.append(os.path.join(rootdir, 'Projects', 'credentials'))
from sqlcfg import projectroot, host, user, passwd

#SOME DATABASE ASSUMPTIONS TO BE AWARE OF
#assumes that there is only one area with a given name in each state.

#database parameters
class Cfg():
    def __init__(self):
        self.projectroot = projectroot
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = 'climbdb2'
        self.charset = 'utf8'
        self.use_unicode = 0
        self.clobber = False
    pass
cfg=Cfg()

#connect to the database with sqlalchemy
engine = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' %(cfg.user, cfg.host, cfg.dbname, cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)

Base = declarative_base()

class AreaTable(Base):
    __tablename__ = 'Area'
    areaid = Column(Integer, primary_key=True, autoincrement=True)
    area = Column(Integer, ForeignKey('Area.areaid'))
    name = Column(String(70))
    url = Column(String(200))
    mainarea = Column(Boolean)
    description = Column(Text) #String(15000)
    elevation = Column(String(70))
    directions = Column(Text) #String(3000)
    maplocation = Column(String(70))
    mapref = Column(String(70))
    region = Column(String(20))
    country = Column(String(20))
    pageviews = Column(String(30))


class ClimbTable(Base):
    __tablename__ = 'Climb'
    climbid = Column(Integer, primary_key=True, autoincrement=True)
    area = Column(Integer, ForeignKey('Area.areaid'))
    region = Column(String(20))
    name = Column(String(70))
    description = Column(Text)#String(10000)
    grade = Column(String(30))
    fa = Column(String(200))
    protection = Column(Text)
    locationdescrip = Column(Text)#String(2000)
    pitch = Column(String(30))
    style = Column(String(30))
    name = Column(String(70))
    url = Column(String(200))
    length = Column(String(30))
    avgstars = Column(String(30))
    pageviews = Column(String(30))
    submittedby = Column(String(70))
    
class ClimberTable(Base):
    __tablename__ = 'Climber'
    climberid = Column(Integer, primary_key=True, autoincrement=True)
    mainarea = Column(Integer, ForeignKey('Area.areaid'))
    name = Column(String(70))
    url = Column(String(200))
    gender = Column(String(30))
    personal = Column(String(200))
    age = Column(Integer)
    favclimbs_parsed = Column(Integer, ForeignKey('Climb.climbid'))
    favclimbs = Column(String(200))
    interests = Column(String(200))
    climbstyles = Column(String(200))
    selfreportgrades = Column(String(70))
    moreinfo = Column(Text)#String(1000)
    trad_l = Column(String(30))
    trad_f = Column(String(30))
    sport_l = Column(String(30))
    sport_f = Column(String(30))
    ice_l = Column(String(30))
    ice_f = Column(String(30))
    boulders = Column(String(30))
    aid_l = Column(String(30))
    aid_f = Column(String(30))
    mixed_l = Column(String(30))
    mixed_f = Column(String(30))
    
class PhotoTable(Base):
    __tablename__ = 'Photo'
    photoid = Column(Integer, primary_key=True, autoincrement=True)
    poster = Column(Integer, ForeignKey('Climber.climberid'))
    climb = Column(Integer, ForeignKey('Climb.climbid'))
    climblink = Column(String(200))
    area = Column(Integer, ForeignKey('Area.areaid'))
    arealink = Column(String(200))
    url = Column(String(200))
    name = Column(String(200))
    date = Column(Date)
    photo = Column(Text)
    
class TicksTable(Base):
    __tablename__ = 'Ticks'
    ticksid = Column(Integer, primary_key=True, autoincrement=True)
    climb = Column(Integer, ForeignKey('Climb.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('Climber.climberid'))
    url = Column(String(200))
    note = Column(Text)#String(5000)
    date = Column(Date)
    name = Column(String(200))
    
class CommentsTable(Base):
    __tablename__ = 'Comments'
    commentsid = Column(Integer, primary_key=True, autoincrement=True)
    climb = Column(Integer, ForeignKey('Climb.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('Climber.climberid'))
    url = Column(String(200))
    comment = Column(Text)#String(10000)
    date = Column(Date)
    name = Column(String(200))
    
class StarsTable(Base):
    __tablename__ = 'Stars'
    starid = Column(Integer, primary_key=True, autoincrement=True)
    starsscore = Column(String(20))
    climb = Column(Integer, ForeignKey('Climb.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('Climber.climberid'))
    url = Column(String(200))
    name = Column(String(200))
    
class GradesTable(Base):
    __tablename__ = 'Grades'
    gradesid = Column(Integer, primary_key=True, autoincrement=True)
    climb = Column(Integer, ForeignKey('Climb.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('Climber.climberid'))
    url = Column(String(200))
    grade = Column(String(30))
    name = Column(String(200))
    
class ToDosTable(Base):
    __tablename__ = 'ToDos'
    todosid = Column(Integer, primary_key=True, autoincrement=True)
    climb = Column(Integer, ForeignKey('Climb.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('Climber.climberid'))
    url = Column(String(200))
    name = Column(String(200))
    
#Create the tables
Base.metadata.create_all(engine)
