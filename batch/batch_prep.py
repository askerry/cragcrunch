# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:31:42 2015

@author: amyskerry
"""
import numpy as np
import pandas as pd
import scipy.stats
from utilities import prep
from utilities import randomdata as rd
from multiprocessing import Pool

################################
#         Misc Cleanup         #
################################

def combinestars(climbdf):
    '''combine extracted and computed averages'''
    newstars=[]
    for index, row in climbdf.iterrows():
        if row['computed_avgstars']<.5:
            climbdf.loc[index,'extracted_avgstars']=row['computed_avgstars']
            newstars.append(row['computed_avgstars'])
        else:
            newstars.append(np.nanmean([row['extracted_avgstars'], row['computed_avgstars']]))
    climbdf['avgstars']=newstars
    return climbdf
    
def dedupsandmissing(climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf):
    '''deal with duplicated/missing areas and climbers'''
    areadf=dedupareas(areadf) 
    climberdf=dedupclimbers(climberdf)
    tickdf= addmissingclimbers(climberdf, tickdf)
    commentdf = addmissingclimbers(climberdf, commentdf)
    gradedf = addmissingclimbers(climberdf, gradedf)
    stardf = addmissingclimbers(climberdf, stardf)
    return climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf
    
def reindexall(hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf):
    '''reindex everything so that id is index'''
    climbdf.index=climbdf.climbid
    areadf.index=areadf.areaid
    climberdf.index=climberdf.climberid
    tickdf.index=tickdf.ticksid
    commentdf.index=commentdf.commentsid
    gradedf.index=gradedf.gradesid
    stardf.index=stardf.starid
    hitsdf.index=hitsdf.hitsid
    return hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf

def renameindices(hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf):
    climbdf.index.rename('index', inplace=True)
    areadf.index.rename('index', inplace=True)
    climberdf.index.rename('index', inplace=True)
    tickdf.index.rename('index', inplace=True)
    commentdf.index.rename('index', inplace=True)
    gradedf.index.rename('index', inplace=True)
    stardf.index.rename('index', inplace=True)
    hitsdf.index.rename('index', inplace=True)
    return hitsdf, climberdf, areadf, climbdf,stardf,commentdf,gradedf,tickdf
    
def quantize_grades(climbdf):
    climbdf['numerizedgrade']=climbdf['grade'].apply(prep.numerizegrades, gradelists=[rd.grades, rd.bouldergrades])
    climbdf['numgrade']=climbdf['grade'].apply(prep.splitgrade, output='num')
    climbdf['lettergrade']=climbdf['grade'].apply(prep.splitgrade, output='letter')
    return climbdf
    

def text_counts(climbdf):
    feature_dict=prep.load_text_feats()
    terms=feature_dict.keys()
    p = Pool(4)
    tuples=[p.apply(prep.text_processing, args=(string, feature_dict)) for string in climbdf['description'].values]
    data=zip(*tuples)
    for tnum,term in enumerate(terms):
        climbdf['t_'+term]=data[tnum]
    return climbdf
    
def summarize_climbers(tickdf, climbdf, climberdf):
    t=pd.merge(tickdf, climbdf[['climbid', 'mainarea', 'region', 'numerizedgrade']], left_on='climb', right_on='climbid', how='right')
    climber_areas=t.groupby('climber')[['mainarea']].apply(lambda x:scipy.stats.mode(x)[0][0][0])
    climber_areas=pd.DataFrame(data={'climberid':climber_areas.index.values, 'mainarea':climber_areas.values})
    climber_regions=t.groupby('climber')[['region']].apply(lambda x:scipy.stats.mode(x)[0][0][0])
    climber_regions=pd.DataFrame(data={'climberid':climber_regions.index.values, 'region':climber_regions.values})
    avg_grade=t.groupby('climber')[['numerizedgrade']].apply(lambda x:np.nanmean(x))
    avg_grade=pd.DataFrame(data={'climberid':avg_grade.index.values, 'avg_grade':avg_grade.values})
    climberdf=pd.merge(climberdf, climber_areas, on='climberid', how='left', suffixes=['_l', ''])
    del climberdf['mainarea_l']
    climberdf=pd.merge(climberdf, climber_regions, on='climberid', how='left')
    climberdf=pd.merge(climberdf, avg_grade, on='climberid', how='left')
    climberdf['region']=climberdf['region'].fillna('World').values
    climberdf['mainarea']=climberdf['mainarea'].fillna(2).values
    climberdf['avg_grade']=climberdf['avg_grade'].fillna(31).values
    return climberdf
    
def add_names(areadf, climbdf):
    areadf=pd.merge(areadf, areadf[['areaid', 'name']], left_on='mainarea', right_on='areaid', how='left', suffixes=['', '_r'])
    areadf=areadf.rename(columns={'name_r':'mainarea_name'})
    climbdf=pd.merge(climbdf, areadf[['areaid', 'name']], left_on='mainarea', right_on='areaid', how='left', suffixes=['', '_r'])
    climbdf=climbdf.rename(columns={'name_r':'mainarea_name'})
    return areadf, climbdf
################################
#       Reduction Steps        #
################################

def dropstyles(climbdf,stardf, commentdf, gradedf, tickdf):
    '''I don't like ice or alpine climbing so I'm not going to worry about them :)'''
    dropids=[]
    mask=climbdf['style'].isin(['Alpine', 'Ice', 'Mixed', 'Chipped', 'Aid'])
    dropids.extend(climbdf[mask].climbid.values)
    dropids.extend(climbdf[climbdf['style']=='nan'].climbid.values)
    mask1=climbdf['style'].isin(['Sport', 'Trad', 'TR'])
    mask2=~climbdf['grade'].map(lambda x:x.startswith('5'))
    dropids.extend(climbdf.loc[mask1 & mask2].climbid.values)
    mask1=climbdf['style']=='Boulder'
    mask2=~climbdf['grade'].map(lambda x:x.startswith('V'))
    dropids.extend(climbdf.loc[mask1 & mask2].climbid.values)
    dclimbs=climbdf.loc[climbdf['climbid'].isin(dropids)]
    climbdf=climbdf.drop(dclimbs.index.values)
    stardf, commentdf, gradedf, tickdf=dropfromothers(dropids, stardf, commentdf, gradedf, tickdf)
    return climbdf,stardf, commentdf, gradedf, tickdf 
    
def dropfromothers(dropids, stardf, commentdf, gradedf, tickdf):
    '''take ids of climbs to drop, and drop them from all other dataframes'''
    stardf=drop(stardf,'climb', dropids)
    commentdf= drop(commentdf,'climb', dropids)
    gradedf=drop(gradedf,'climb', dropids)
    tickdf=drop(tickdf,'climb', dropids)
    return stardf, commentdf, gradedf, tickdf
    
def drop(df,col, dropids):
    '''drop specified climbs from df'''
    keeperindices=[c for c in df[col] if c not in dropids]
    return df.loc[df[col].isin(keeperindices)]
    
def dropclimbs(climbdf, hitsdf, stardf, commentdf, gradedf, tickdf):
    '''drop climbs that aren't in climbdb'''
    hitsdf=hitsdf[hitsdf['climb'].isin(climbdf.climbid.values)]
    stardf=stardf[stardf['climb'].isin(climbdf.climbid.values)]
    commentdf=commentdf[commentdf['climb'].isin(climbdf.climbid.values)]
    gradedf=gradedf[gradedf['climb'].isin(climbdf.climbid.values)]
    tickdf=tickdf[tickdf['climb'].isin(climbdf.climbid.values)]
    return hitsdf, stardf, commentdf, gradedf, tickdf
    
def dropungraded(climbdf,stardf, commentdf, gradedf, tickdf):
    '''drop climbs that don't have grades'''
    dropids=climbdf.loc[climbdf['grade']=='nan'].climbid.values
    climbdf=climbdf.loc[climbdf['grade']!='nan']
    stardf, commentdf, gradedf, tickdf=dropfromothers(dropids, stardf, commentdf, gradedf, tickdf)
    return climbdf,stardf, commentdf, gradedf, tickdf
    
def limittoUSA(climbdf, areadf):
    '''limit to climbs in  USA'''
    climbdf=climbdf[~climbdf['region'].isin(['Africa', 'Europe', 'Australia', 'Oceania', 'Asia', 'South America'])]
    internationalid=areadf[areadf.name=='International'].area.values[0]
    areadf=areadf[areadf.country=='USA']
    climbdf=climbdf[climbdf['area']!=internationalid]
    return climbdf, areadf
    
def limit2popular(hitsdf,climbdf, stardf, commentdf, gradedf, tickdf, minthresh=5):
    selclimbs=hitsdf.groupby('climb').count()['climber']
    selclimbs=[v for v in selclimbs[selclimbs>minthresh].index.values if ~np.isnan(v)]
    popclimbdf=climbdf.loc[selclimbs,:]
    hitsdf, stardf, commentdf, gradedf, tickdf=dropclimbs(popclimbdf, hitsdf, stardf, commentdf, gradedf, tickdf)
    print "beginning with %s unique climbs" %(len(climbdf))
    print "limited to %s climbs by restricting to climbs with >%s climber entries" %(len(popclimbdf),minthresh)
    return popclimbdf, hitsdf, stardf, commentdf, gradedf, tickdf



################################
#  Duplicates/Missing Values   #
################################

def dedupareas(df):
    '''drop duplicate areas (keeping one with full info)'''
    dups=df[df.duplicated('name')]
    delete=[]
    for dindex,dup in dups.iterrows():
        if dup['url'].count('/')>3:
            delete.append(dup['areaid'])
    indices=df.loc[df['areaid'].isin(delete)].index.values
    df=df.drop(indices)
    return df
    
def dedupclimbers(climberdf):
    '''drop duplicate climbs (keeping one with full info)'''    
    dupnames=climberdf.loc[climberdf['name'].duplicated()].name.values
    for d in dupnames:
        climber=climberdf.loc[climberdf['name']==d]
        try:
            dropid=climber.loc[climber['url']=='nan'].index.values[0]
        except:
            dropid=climber.iloc[0,:].values[0]
        climberdf=climberdf[climberdf['climberid']!=dropid]
    return climberdf   
    
def addmissingclimbers(climberdf, df):
    '''some climber info is missing from its dependent dfs... add climber data from climberdf'''
    urls=df.loc[np.isnan(df['climber']),'urlname'].values
    indices=df[np.isnan(df['climber'])].index.values
    for urln,url in enumerate(urls):
        matches=climberdf.loc[climberdf['urlname']==url].climberid.values
        if len(matches)>0:
            df.loc[indices[urln],'climber']=matches[0]
    return df
    
################################
#       Area Processing        #
################################ 

def list_states_and_mains(areadf):
    '''take an area and define the region for it based on it's parent'''
    states=areadf[areadf['region']=='World'].name.values
    stateids=areadf[areadf['region']=='World'].areaid.values
    mainareas=areadf.loc[areadf['area'].isin(stateids)].areaid.values
    mainareas=extend_mains(mainareas, areadf)
    return states, stateids, mainareas
        
def extend_mains(mainareas, areadf):
    othermains=[]
    for m in mainareas:
        othermains=prep.check_one_level_down(m, othermains, areadf)
    return list(mainareas)+list(othermains)
    
def add_mains_to_areas(mainareas, areadf):
    areadf['mainarea']=np.nan
    for areaid in mainareas:
        subs=prep.getsubareas(areaid, areadf=areadf)
        areadf.loc[areadf['areaid'].isin(subs),'mainarea']=areaid
    return areadf

    
def add_states_and_mains_to_climbs(climbdf, areadf):
    '''added regions to climbs and dropped climbs missing regions'''
    climbdf=pd.merge(climbdf, areadf[['areaid','region', 'mainarea']], left_on='area', right_on='areaid', how='inner')
    climbdf=climbdf.rename(columns={'region_y':'region'})
    del climbdf['region_x']
    climbdf=pd.merge(climbdf, areadf[['areaid','name']], left_on='area', right_on='areaid', how='left')
    climbdf=climbdf.rename(columns={'name_x':'name','name_y':'area_name'})
    return climbdf
    

def getclimberareas(hitsdf, climbdf, climberdf):
    '''get all mainareas that a climber has climbd in'''
    for c in climberdf.climberid.values:
        climbids=hitsdf[hitsdf['climber']==c]['climb'].values
        areas=climbdf.loc[climbids,'mainarea'].values
        numareas=len(set(areas))
        try:
            m=scipy.stats.mode(areas)[0][0]
        except:
            m=np.nan
        climberdf.loc[c,'mainarea']=m
        climberdf.loc[c,'numareas']=numareas
    return climberdf

################################
#      Ghetto Hack Fixes       #
################################

def fixclimbers(climberdf, hitsdf):
    '''some climbers are duped such that one entry has attributes and other entry has foreign key from other table pointing to it. merge these to preserve the foreign keys'''
    emptyclimbers=climberdf.loc[climberdf['url']=='nan'].climberid.values
    call=[int(el) for el in hitsdf.climber.values]
    for c in emptyclimbers:
        name=climberdf.loc[climberdf['climberid']==c,'name'].values[0]
        index=climberdf.loc[climberdf['climberid']==c].index.values[0]
        cs=climberdf.loc[climberdf['name']==name]
        csindex=cs.loc[cs['climberid']!=c].index.values
        csid=cs.loc[cs['climberid']!=c].climberid.values
        if len(csid)>0 and csid[0] not in call:
            climberdf.loc[csindex[0],'climberid']=c
            climberdf=climberdf.drop([index])
    climberdf=climberdf[~climberdf['climberid'].isnull()]
    return climberdf
    
def fixstars(stardf, climbdf):
    '''avg stars can come from the html extracted (avg in full MP database at time of scraping) or computed from the individual ratings extracted. clarify this'''
    climbdf['extracted_avgstars']=climbdf.loc[:,'avgstars'].values
    stardf=stardf[stardf['climb'].isin(climbdf.climbid.values)]
    climbstars=stardf.groupby('climb').mean().reset_index()
    ids=[int(val) for val in climbstars.loc[:,'climb'].values]
    stars=stardf.groupby('climb').mean()['starsscore'].values
    climbdf.loc[ids,'computed_avgstars']=stars
    return climbdf
    