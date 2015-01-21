# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 12:49:34 2015

@author: amyskerry
"""

import scipy.stats
import numpy as np
import clean
import random as rd

def getratingcounts(climbid, sdf=None):
    '''return number of people who have rating a climb'''
    relsdf=sdf[sdf['climb']==climbid]
    return len(relsdf), np.std(relsdf.starsscore)


def getnonuserstar(climbid, userid, sdf=None):
    '''return avg rating of a climb for all users excluding that user'''
    climbdf=sdf[sdf['climb']==climbid]
    nonuserdf=climbdf[climbdf['climber']!=userid]
    avg=nonuserdf.starsscore.mean()
    print avg
    std=nonuserdf.starsscore.std()
    return avg, std

def getstates(areadf):
    '''take an area and define the region for it based on it's parent'''
    states=areadf[areadf['region']=='World'].name.values
    stateids=areadf[areadf['region']=='World'].areaid.values
    statedict={}
    for sn,s in enumerate(states):
        statedict[s]=getsubareas(areadf, stateids[sn])
    mainareadf=areadf.loc[areadf['area'].isin(stateids)]
    return states, stateids, statedict, mainareadf
    
def computerelativestar(stardf,climbdf):
    '''for each climber, calculate the difference between their rating and the average rating'''
    climbids=stardf['climb'].values
    starids=stardf['starid'].values
    averages=climbdf.loc[climbids,'avgstars'].values
    diffs=stardf['starsscore'].values-averages
    stardf.loc[starids,'relative_star']=diffs
    return stardf
    
def normalizetoindividual(indstars):
    indstars['zscored_star_relative']=(indstars['relative_star'].values-indstars['relative_star'].mean())/indstars['relative_star'].std()
    indstars['zscored_star']=(indstars['starsscore'].values-indstars['starsscore'].mean())/indstars['starsscore'].std()
    return indstars
    
def relativegrade(gid, climbid, grade, cdf=None, ndictgrades={}):
    if climbid in cdf.index.values:
        consensus=cdf.loc[climbid,'grade']
        consensus_rank=ndictgrades[consensus]
        ind_rank=ndictgrades[grade]
        return float(ind_rank)-float(consensus_rank)
        
def computerelativegrades(climbdf, gradedf):
    allgrades=list(gradedf['grade'].unique())+list(climbdf['grade'].unique())
    ndictgrades={c:clean.numerizegrades(c, gradelists=[rd.grades, rd.bouldergrades]) for c in allgrades}
    gradedf['rankdiff']=gradedf.apply(lambda x:relativegrade(x['gradesid'], x['climb'], x['grade'], cdf=climbdf, ndictgrades=ndictgrades), axis=1)
    return gradedf    
    
def addmainarea(areaid, areadf, climbdf):
    '''takes a given area and finds the highest level parent area that contains it'''
    ids=getsubareas(areadf, areaid)
    areas=areadf.loc[areadf['area'].isin(ids)].index.values
    climbs=climbdf.loc[climbdf['area'].isin(ids)].index.values
    areadf.loc[areas,'mainarea']=areaid
    climbdf.loc[climbs,'mainarea']=areaid
    return areadf,climbdf
    
def getsubareas(areadf, areaid):
    '''get children areas'''
    subareasdf=areadf.loc[areadf['area']==areaid]
    subareaids=list(subareasdf['areaid'].values)
    for index, area in subareasdf.iterrows():
        subareaids.extend(getsubareas(areadf, area['areaid']))
    return subareaids
    
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
    
def getstatesandmainareas(full_areadf, full_climbdf):
    '''get state and main area for each climb'''
    states, stateids, statedict, mainareadf=getstates(full_areadf)
    slist=[stateids[list(states).index(el)] if el in states else np.nan for el in full_areadf['region'].values]
    full_areadf['mainarea']=slist #set default mainarea as state
    slist=[stateids[list(states).index(el)] if el in states else np.nan for el in full_climbdf['region'].values]
    full_climbdf['mainarea']=slist
    for i in mainareadf['areaid'].values:
        full_areadf,full_climbdf=addmainarea(i, full_areadf, full_climbdf)
    print "identified main areas/parks for subareas"
    return states, stateids, statedict, mainareadf, full_areadf, full_climbdf
    
'''    
def computegradevariability(climbdf, gradedf):
    grade_std=gradedf.groupby('climb').std()['rankdiff'].values
    climbids=gradedf.groupby('climb').mean().index.values
    climbdf.loc[climbids,'grade_std']=grade_std
    return climbdf
    
def computeclimbstiffness(climbdf, gradedf, climberdf, minnumberofclimbers=5):
    variable_climbids=climbdf.loc[climbdf['grade_std']>.5].climbid.values
    for c in variable_climbids:
        climbarea=climbdf.loc[c,'mainarea']
        grades=gradedf[gradedf['climb']==c]
        climbers=grades['climber'].values
        areas=climberdf.loc[climbers,'mainarea'].values
        grades['local']=areas==climbarea
        foreignlocal=grades.groupby('local').mean()['rankdiff']
        foreignlocalcounts=grades.groupby('local').count()['rankdiff'].values
        if len(foreignlocal.index.values)==2:
            if np.all(foreignlocalcounts>=minnumberofclimbers):
                stiffness=foreignlocal.loc[False]-foreignlocal.loc[True]
                forgeigngrade=foreignlocal.loc[False]
                localgrade=foreignlocal.loc[True]
            else:
                stiffness=np.nan
                forgeigngrade=np.nan
                localgrade=np.nan
        else:
            stiffness=np.nan
            forgeigngrade=np.nan
            localgrade=np.nan
        climbdf.loc[c,'foriegn_grade']=forgeigngrade
        climbdf.loc[c,'local_grade']=localgrade
        climbdf.loc[c,'stiffness']=stiffness
    return climbdf
    
    
def computeareastiffness(climbdf, areadf):
    local_grade=climbdf.groupby('mainarea').mean()['local_grade']
    foriegn_grade=climbdf.groupby('mainarea').mean()['foriegn_grade']
    areastiffness=climbdf.groupby('mainarea').mean()['stiffness']
    areaindices=climbdf.groupby('mainarea').mean().index.values
    areadf.loc[areaindices,'stiffness']=areastiffness
    areadf.loc[areaindices,'foriegn_grade']=foriegn_grade
    areadf.loc[areaindices,'local_grade']=local_grade
    return areadf
   
    

def summarizesubmitters(climbdf, climberdf, hitsdf):
    submittercounts=climbdf.groupby('submittedby').count()[['climbid']].dropna()
    submittercounts=submittercounts[~np.isnan(submittercounts)]
    submittercounts.rename(columns={'climbid':'climbcounts'}, inplace=True)
    nummainareas,nummainregions,climberids=[],[],[]
    for s in submittercounts.index.values:
        climberid=climberdf.loc[climberdf['name']==s,'climberid'].values
        if len(climberid)>0:
            climberid=climberid[0]
            climbs=hitsdf.loc[hitsdf['climber']==climberid,'climb']
            climbs=climbdf.loc[climbs,:]
            nummainareas.append(len(climbs.mainarea.unique()))
            nummainregions.append(len(climbs.region.unique()))
            climberids.append(climberid)
        else:
            nummainareas.append(np.nan)
            nummainregions.append(np.nan)
            climberids.append(np.nan)
    submittercounts['mainareas']=nummainareas
    submittercounts['nummainregions']=nummainregions
    submittercounts['climberid']=climberids
    submittercounts=submittercounts.reset_index()
    return submittercounts
    
def getnumbers(mainareadf, climberdf, climbdf, hitsdf):
    mainareadf['numclimbers']=0.0
    mainareadf['numlocal']=0.0
    mainareadf['numforeign']=0.0
    for index, row in hitsdf.iterrows():
        climb,climber=int(row['climb']),int(row['climber'])
        if climb in climbdf.index:
            area=climbdf.loc[climb,'mainarea']
            if ~np.isnan(area):
                area=int(area)
                if climber in climberdf.index:
                    climberhome=float(climberdf.loc[climber,'mainarea'])
                    if ~np.isnan(climberhome):
                        climberhome=int(climberhome)
                    if area in mainareadf.index:
                        mainareadf.loc[area, 'numclimbers']=mainareadf.loc[area, 'numclimbers']+1
                        if area==climberhome:
                            mainareadf.loc[area, 'numlocal']=mainareadf.loc[area, 'numlocal']+1
                        else:
                            mainareadf.loc[area, 'numforeign']=mainareadf.loc[area, 'numforeign']+1
    for x in ['numclimbers','numlocal','numforeign']:
        mainareadf.loc[mainareadf[x]==0,x]==np.nan
    return mainareadf
    
def makeclimberxareadf(mainareadf, climbdf, hitsdf, climberdf):
    #creates df of climber x area they have climbed in (val = number of hits at the location)
    areas=pd.DataFrame(columns=[a for a in mainareadf.areaid.values])
    climberxareadf=areas.append(climberdf[['climberid','name', 'mainarea']]).fillna(0)
    climberxareadf.index=climberxareadf.climberid.values
    for a in mainareadf.areaid.values:
        climbs=climbdf.loc[climbdf['mainarea']==a,'climbid'].values
        relhits=hitsdf.loc[hitsdf['climb'].isin(climbs)]
        climbercounts=relhits.groupby('climber').count()
        climbercounts=climbercounts.loc[[c for c in climbercounts.index.values if c in climberxareadf.index],:]
        climberxareadf.loc[climbercounts.index.values,a]=climbercounts.climb.values
    climberxareadf=climberxareadf[climberxareadf['name']!=0]
    return climberxareadf
'''