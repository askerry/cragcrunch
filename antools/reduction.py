# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:31:42 2015

@author: amyskerry
"""
import numpy as np

def dropstyles(climbdf,stardf, commentdf, gradedf, tickdf, tododf):
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
    stardf, commentdf, gradedf, tickdf, tododf=dropfromothers(dropids, stardf, commentdf, gradedf, tickdf, tododf)
    return climbdf,stardf, commentdf, gradedf, tickdf, tododf 
    
def dropfromothers(dropids, stardf, commentdf, gradedf, tickdf, tododf):
    '''take ids of climbs to drop, and drop them from all other dataframes'''
    stardf=drop(stardf,'climb', dropids)
    commentdf= drop(commentdf,'climb', dropids)
    gradedf=drop(gradedf,'climb', dropids)
    tickdf=drop(tickdf,'climb', dropids)
    tododf=drop(tododf,'climb', dropids)
    return stardf, commentdf, gradedf, tickdf, tododf
    
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
    
def dropungraded(climbdf,stardf, commentdf, gradedf, tickdf, tododf):
    '''drop climbs that don't have grades'''
    dropids=climbdf.loc[climbdf['grade']=='nan'].climbid.values
    climbdf=climbdf.loc[climbdf['grade']!='nan']
    stardf, commentdf, gradedf, tickdf, tododf=dropfromothers(dropids, stardf, commentdf, gradedf, tickdf, tododf)
    return climbdf,stardf, commentdf, gradedf, tickdf, tododf
    
def limittoUSA(climbdf, areadf):
    '''limit to climbs in  USA'''
    climbdf=climbdf[~climbdf['region'].isin(['Africa', 'Europe', 'Australia', 'Oceania', 'Asia', 'South America'])]
    internationalid=areadf[areadf.name=='International'].area.values[0]
    areadf=areadf[areadf.country=='USA']
    climbdf=climbdf[climbdf['area']!=internationalid]
    return climbdf, areadf
    
def limit2popular(full_hitsdf,full_climbdf, full_stardf, full_commentdf, full_gradedf, full_tickdf, minthresh=5):
    selclimbs=full_hitsdf.groupby('climb').count()['climber']
    selclimbs=[v for v in selclimbs[selclimbs>minthresh].index.values if ~np.isnan(v)]
    popclimbdf=full_climbdf.loc[selclimbs,:]
    full_hitsdf, full_stardf, full_commentdf, full_gradedf, full_tickdf=dropclimbs(popclimbdf, full_hitsdf, full_stardf, full_commentdf, full_gradedf, full_tickdf)
    print "beginning with %s unique climbs" %(len(full_climbdf))
    print "limited to %s climbs by restricting to climbs with >%s climber entries" %(len(popclimbdf),minthresh)
    return popclimbdf, full_hitsdf, full_stardf, full_commentdf, full_gradedf, full_tickdf