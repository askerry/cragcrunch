# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:15:27 2015

@author: amyskerry
"""
import numpy as np




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
            dropid=climber.iloc[0,:].index.values[0]
        climberdf=climberdf.drop(dropid)
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
    