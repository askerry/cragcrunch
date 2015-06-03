# -*- coding: utf-8 -*-
"""
Created on Wed May 27 20:19:21 2015

@author: amyskerry
"""
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import logging
import sys
sys.path.append('..')
from  utilities import prep
import batch_prep as bp

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def load_data(cfg):
    con = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' % (cfg.user, cfg.host, cfg.dbname, cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)
    climbdf = pd.read_sql("SELECT * from Climb", con)
    climbdf=climbdf[['name']+[el for el in climbdf.columns.tolist() if el!='name']] #moving name first
    areadf = pd.read_sql("SELECT * from Area", con)
    climberdf = pd.read_sql("SELECT * from Climber", con)
    tickdf = pd.read_sql("SELECT * from Ticks", con)
    commentdf = pd.read_sql("SELECT * from Comments", con)
    gradedf = pd.read_sql("SELECT * from Grades", con)
    stardf = pd.read_sql("SELECT * from Stars", con)
    logging.info('data loaded')
    return climbdf, areadf, climberdf, tickdf, commentdf, gradedf, stardf


def cleandf(df):
    '''apply various functions to clean string inputs from html'''
    nanvalues=['','None','unavailable', None]
    df=df.applymap(lambda x:np.nan if x in nanvalues else x)
    for col in df.columns:
        if col in ('climbid', 'areaid', 'climberid', 'ticksid', 'commentsid', 'gradesid', 'starid', 'climb', 'climber', 'area'):
            df[col]=df[col].convert_objects(convert_numeric=True).values
        elif col in ('starsscore', 'age', 'avgstars'):
            df[col]=df[col].convert_objects(convert_numeric=True).values
        elif col =='pageviews':
            df[col]=df[col].apply(prep.removecomma)
        elif col=='maplocation':
            df['latitude']=df[col].apply(prep.getlat)
            df['longitude']=df[col].apply(prep.getlong)
            del df['maplocation']
        elif col in ('elevation', 'length'):
            df[col]=df[col].apply(prep.striplength)
        elif col=='pitch':
            df[col]=df[col].apply(prep.pitch)
        else:
            df[col]=df[col].apply(prep.strip)
        if col=='url':
            df['urlname']=df[col].apply(prep.extractname)
        if col=='style':
            df[col]=df[col].apply(prep.mergeiceandsnow)
        if col =='pitch':
            df[col]=df[col].apply(prep.strippitch)
    return df


def create_hitdf(tickdf, commentdf, gradedf, stardf):
    
    hitsdf=pd.concat([stardf[['climb','climber', 'urlname']], tickdf[['climb','climber', 'urlname']],commentdf[['climb','climber','urlname']],gradedf[['climb','climber','urlname']]])
    hitsdf=hitsdf.drop_duplicates()
    hitsdf=hitsdf.loc[~np.isnan(hitsdf.climber.values)]
    hitsdf.index=range(len(hitsdf))
    hitsdf['hitsid']=hitsdf.index.values
    return hitsdf

    
def area_parsing(areadf, climbdf):
    states, stateids, mainareas=bp.list_states_and_mains(areadf)
    mainareas=bp.extend_mains(mainareas, areadf)
    areadf=bp.add_mains_to_areas(mainareas, areadf)
    climbdf=bp.add_states_and_mains_to_climbs(climbdf, areadf)
    areadf, climbdf=bp.add_names(areadf, climbdf)
    logging.info("parsed area information")
    return areadf, climbdf
    
def write_data(cfg, climbdf, areadf, climberdf, tickdf, commentdf, gradedf, stardf, hitsdf, chunksize=1000):
    #save prepped data to sql
    con = create_engine('mysql://%s@%s/%s?charset=%s&use_unicode=%s&passwd=%s' % (cfg.user, cfg.host, cfg.dbname+'_prepped', cfg.charset, cfg.use_unicode, cfg.passwd), pool_recycle=3600)
    areadf.to_sql('area_prepped', con, if_exists='replace', chunksize=chunksize)
    climberdf.to_sql('climber_prepped', con,if_exists='replace', chunksize=chunksize)
    tickdf.to_sql('ticks_prepped', con, if_exists='replace', chunksize=chunksize)
    commentdf.to_sql('comments_prepped', con, if_exists='replace', chunksize=chunksize)
    gradedf.to_sql('grades_prepped', con, if_exists='replace', chunksize=chunksize)
    stardf.to_sql('stars_prepped', con, if_exists='replace', chunksize=chunksize)
    hitsdf.to_sql('hits_prepped', con, if_exists='replace', chunksize=chunksize)
    climbdf.to_sql('climb_prepped', con, if_exists='replace', chunksize=chunksize)
    logging.info("wrote to database {}".format(cfg.dbname+'_prepped'))
    
        
if __name__=='__main__':
    
    sys.path.append('../cfg')
    from cfg.database_cfg import cfg
    
    #parse database input
    cfg.dbname=sys.argv[1]
    
    #load in the data
    climbdf, areadf, climberdf, tickdf, commentdf, gradedf, stardf=load_data(cfg)
    
    #basic cleaning    
    climbdf=cleandf(climbdf)
    areadf=cleandf(areadf) 
    climberdf=cleandf(climberdf) 
    tickdf=cleandf(tickdf) 
    commentdf=cleandf(commentdf) 
    gradedf=cleandf(gradedf) 
    stardf=cleandf(stardf) 
    logging.info("performed dataframe initial cleaning ({} climbs)".format(len(climbdf)))
    
    #initial reduction steps
    climbdf,stardf,commentdf,gradedf,tickdf=bp.dropstyles(climbdf,stardf,commentdf,gradedf,tickdf)
    climbdf, areadf=bp.limittoUSA(climbdf, areadf)
    climbdf,stardf,commentdf,gradedf,tickdf=bp.dropungraded(climbdf,stardf,commentdf,gradedf,tickdf)
    climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf=bp.dedupsandmissing(climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf)
    logging.info("performed data reduction ({} climbs)".format(len(climbdf)))
      
    #create climber x climb matrix
    hitsdf=create_hitdf(tickdf, commentdf, gradedf, stardf)
    
    #misc fixes  
    climberdf=bp.fixclimbers(climberdf, hitsdf)
    hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf=bp.reindexall(hitsdf,climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf)
    #random cleanup hacks
    stardf.starsscore=stardf.starsscore-1
    climberdf.loc[climberdf['age']>120, 'age']=np.nan #catch some jokesters
    #limit all dfs to the climbs we currently have in climbdf
    hitsdf, stardf, commentdf, gradedf, tickdf=bp.dropclimbs(climbdf, hitsdf, stardf, commentdf, gradedf, tickdf)
    climbdf=bp.quantize_grades(climbdf)
    logging.info("performed additional cleaning ({} climbs)".format(len(climbdf)))
    
    
    #area parsing
    areadf, climbdf=area_parsing(areadf, climbdf)
    hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf=bp.reindexall(hitsdf,climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf)
    hitsdf=hitsdf[hitsdf['climb'].isin(climbdf['climbid'].values)]
    
    climberdf=bp.summarize_climbers(tickdf, climbdf, climberdf)
    
    #cleanup stars
    climbdf=bp.fixstars(stardf, climbdf)
    climbdf=bp.combinestars(climbdf)
    climbdf['roundedstars']=climbdf['avgstars'].apply(np.round) 
    morecols=climbdf['climbid'].apply(prep.rating_confidence, sdf=stardf)
    climbdf['starcounts']=[x[0] for x in morecols.values]
    climbdf['starstd']=[x[1] for x in morecols.values]
    logging.info("performed star rating clean up")
    
    #final reduction for consistency
    hitsdf, stardf, commentdf, gradedf, tickdf=bp.dropclimbs(climbdf, hitsdf, stardf, commentdf, gradedf, tickdf)
    hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf=bp.renameindices(hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf)
    hitsdf=hitsdf[hitsdf['climber'].isin(climberdf.climberid.unique())]
    logging.info("final reduction to ({} climbs)".format(len(climbdf)))
    
    climbdf=bp.text_counts(climbdf)
    
    #write to database
    write_data(cfg, climbdf, areadf, climberdf, tickdf, commentdf, gradedf, stardf, hitsdf)