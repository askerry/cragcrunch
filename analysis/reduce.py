# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:31:42 2015

@author: amyskerry
"""

def dropstyles(climbdf,stardf, commentdf, gradedf, tickdf, tododf):
    '''I don't like ice or alpine climbing so I'm not going to worry about them :)'''
    dropids=[]
    mask=climbdf['style'].isin(['Alpine', 'Ice', 'Mixed', 'Chipped']).values
    dropids.extend(climbdf.loc[mask].climbid.values)
    mask1=climbdf['style'].isin(['Sport', 'Trad', 'TR']).values
    mask2=~climbdf['grade'].map(lambda x:x.startswith('5')).values
    dropids.extend(climbdf.loc[mask1 & mask2].climbid.values)
    mask1=climbdf['style']=='Boulder'
    mask2=~climbdf['grade'].map(lambda x:x.startswith('V')).values
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
    keeperindices=[c for c in df[col] if c not in dropids]
    return df.loc[df[col].isin(keeperindices)]