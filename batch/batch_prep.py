# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:31:42 2015

@author: amyskerry
"""
import numpy as np

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
    
def dedupsandmissing(full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf):
    '''deal with duplicated/missing areas and climbers'''
    full_areadf=clean.dedupareas(full_areadf) 
    full_climberdf=clean.dedupclimbers(full_climberdf)
    full_tickdf= clean.addmissingclimbers(full_climberdf, full_tickdf)
    full_commentdf = clean.addmissingclimbers(full_climberdf, full_commentdf)
    full_gradedf = clean.addmissingclimbers(full_climberdf, full_gradedf)
    full_tododf= clean.addmissingclimbers(full_climberdf, full_tododf)
    full_stardf = clean.addmissingclimbers(full_climberdf, full_stardf)
    return full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf
    
def reindexall(full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf):
    '''reindex everything so that id is index'''
    full_climbdf.index=full_climbdf.climbid
    full_areadf.index=full_areadf.areaid
    full_climberdf.index=full_climberdf.climberid
    full_tickdf.index=full_tickdf.ticksid
    full_commentdf.index=full_commentdf.commentsid
    full_gradedf.index=full_gradedf.gradesid
    full_stardf.index=full_stardf.starid
    full_tododf.index=full_tododf.todosid
    full_hitsdf.index=full_hitsdf.hitsid
    return full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf

def renameindices(full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf, mainareadf):
    full_climbdf.index.rename('index', inplace=True)
    full_areadf.index.rename('index', inplace=True)
    full_climberdf.index.rename('index', inplace=True)
    full_tickdf.index.rename('index', inplace=True)
    full_commentdf.index.rename('index', inplace=True)
    full_gradedf.index.rename('index', inplace=True)
    full_stardf.index.rename('index', inplace=True)
    full_tododf.index.rename('index', inplace=True)
    full_hitsdf.index.rename('index', inplace=True)
    mainareadf.index.rename('index', inplace=True)
    return full_hitsdf, full_climberdf, full_areadf, full_climbdf,full_stardf,full_commentdf,full_gradedf,full_tickdf,full_tododf,mainareadf

################################
#       Reduction Steps        #
################################

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