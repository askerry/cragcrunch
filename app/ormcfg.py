from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import Column, Integer, Float, String, Boolean, Date, ForeignKey, Text
from config import dirname
import os
import pickle
import json
import collections
from config import fulldir

attribute_file=fulldir+'/cfg/attributes.json'
with open(attribute_file, 'r') as f:
        j=f.read()
attributes=json.loads(j, object_pairs_hook=collections.OrderedDict) 

Base = declarative_base()

class AreaTable(Base):
    __tablename__ = 'area_prepped'
    areaid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    area = Column(Float, ForeignKey('area_prepped.areaid'))
    name = Column(String(70))
    url = Column(String(200))
    mainarea = Column(String(30))
    description = Column(Text)  # String(15000)
    elevation = Column(Float)
    directions = Column(Text)  # String(3000)
    latitude = Column(Float)
    longitude = Column(Float)
    mapref = Column(String(70))
    region = Column(String(20))
    country = Column(String(20))
    pageviews = Column(Float)
    mainarea_name = Column(String(70))


class ClimbTable(Base):
    __tablename__ = 'climb_prepped'
    climbid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    area = Column(Integer, ForeignKey('area_prepped.areaid'))
    region = Column(String(20))
    name = Column(String(70))
    mainarea = Column(Integer)
    description = Column(Text)  # String(10000)
    grade = Column(String(30))
    fa = Column(String(200))
    protection = Column(Text)
    locationdescrip = Column(Text)  # String(2000)
    pitch = Column(String(30))
    style = Column(String(30))
    name = Column(String(70))
    url = Column(String(200))
    length = Column(String(30))
    avgstars = Column(String(30))
    pageviews = Column(String(30))
    submittedby = Column(String(70))
    numerizedgrade = Column(Float)
    mainarea_name = Column(String(70))
    area_name = Column(String(70))
for attr in attributes:
    setattr(ClimbTable, 't_'+attr, Column(Float))


class ClimberTable(Base):
    __tablename__ = 'climber_prepped'
    climberid = Column(Integer, primary_key=True, autoincrement=True, nullable=False, index=True)
    mainarea = Column(Integer, ForeignKey('area_prepped.areaid'))
    name = Column(String(70))
    url = Column(String(200))
    gender = Column(String(30))
    personal = Column(String(200))
    age = Column(Integer)
    favclimbs_parsed = Column(Integer, ForeignKey('climb_prepped.climbid'))
    favclimbs = Column(String(200))
    interests = Column(String(200))
    climbstyles = Column(String(200))
    selfreportgrades = Column(String(70))
    moreinfo = Column(Text)  # String(1000)
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
    region = Column(String(70))


class TicksTable(Base):
    __tablename__ = 'ticks_prepped'
    ticksid = Column(Integer, primary_key=True, autoincrement=True)
    climb = Column(Integer, ForeignKey('climb_prepped.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('climber_prepped.climberid'))
    url = Column(String(200))
    note = Column(Text)  # String(5000)
    date = Column(Date)
    name = Column(String(200))


class CommentsTable(Base):
    __tablename__ = 'comments_prepped'
    commentsid = Column(Integer, primary_key=True, autoincrement=True)
    climb = Column(Integer, ForeignKey('climb_prepped.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('climber_prepped.climberid'))
    url = Column(String(200))
    comment = Column(Text)  # String(10000)
    date = Column(Date)
    name = Column(String(200))


class StarsTable(Base):
    __tablename__ = 'stars_prepped'
    starid = Column(Integer, primary_key=True, autoincrement=True)
    starsscore = Column(String(20))
    climb = Column(Integer, ForeignKey('climb_prepped.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('climber_prepped.climberid'))
    url = Column(String(200))
    name = Column(String(200))


class GradesTable(Base):
    __tablename__ = 'grades_prepped'
    gradesid = Column(Integer, primary_key=True, autoincrement=True)
    climb = Column(Integer, ForeignKey('climb_prepped.climbid'))
    climblink = Column(String(200))
    climber = Column(Integer, ForeignKey('climber_prepped.climberid'))
    url = Column(String(200))
    grade = Column(String(30))
    name = Column(String(200))

class HitsTable(Base):
    __tablename__ = 'hits_prepped'
    hitsid = Column(Integer, primary_key=True,)
    climb = Column(Integer, ForeignKey('climb_prepped.climbid'))
    climber = Column(Integer, ForeignKey('climber_prepped.climberid'))
    urlname = Column(String(200))

class ProfileTable(Base):
    __tablename__ = 'user_profiles'
    userid = Column(Integer, ForeignKey('climber_prepped.climberid'), primary_key=True, autoincrement=True)
    name = Column(String(70))
    password = Column(String(30))
    region = Column(String(50))
    mainarea = Column(Integer)
    preferences=Column(String(500))

