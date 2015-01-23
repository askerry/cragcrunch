# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:15:27 2015

@author: amyskerry
"""
import numpy as np


################################
#    Basic String Cleaning     #
################################

def removecomma(pageview):
    '''fix a issue with comma in pageview string'''
    if pageview:
        try:
            return float(pageview)
        except:
            return float(''.join(pageview.split(',')))
    else:
        return np.nan
        
def getlat(loc):
    '''get latitiude from loc string'''
    if type(loc)==float:
        return loc
    else:
        if loc:
            return float(loc.split(',')[0])
        else:
            return loc
            
def getlong(loc):
    '''get longitude from loc string'''
    if type(loc)==float:
        return loc
    else:
        if loc:
            return float(loc.split(',')[1])
        else:
            return loc
            
def striplength(lengthstr):
    '''clean feet symbol from route length where applicable'''
    if lengthstr:
        try:
            return float(lengthstr[:-1])
        except:
            return np.nan
    else:
        return lengthstr
        
def extractname(string):
    '''get user name from url string'''
    try:
        string=string[string.index('/u/')+3:]
        return string[:string.index('/')]
    except:
        return np.nan
        
def pitch(pitchstr):
    '''clean pitches'''
    if type(pitchstr)==str:
        p=[el for el in pitchstr if el.isdigit()]
        return float(''.join(p))
    else:
        return pitchstr      
        
def strip(string):
    '''strip white space from string'''
    try:
        return str(string.strip())
    except:
        return str(string)
        
def mergeiceandsnow(style):
    '''combine ice climbing and snow into one'''
    if style=='Snow':
        return 'Ice'
    else: 
        return style
        
def strippitch(pitch):
    try:
        nump=int(pitch[:pitch.index(' ')])
    except:
        try:
            nump=int(pitch)
        except:
            nump=np.nan
    return nump

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
    
################################
#      Misc Grade Cleanups     #
################################

def numerizegrades(grade, gradelists=()):
    '''convert grade to numeric scale'''
    num=np.nan
    for l in gradelists:
        if grade in l:
            return l.index(grade)
    return num
    
def splitgrade(grade,output='num'):
    '''split grade into numeric and letter values'''
    if grade:
        num=grade
        letter=''
        if grade=='Easy 5th':
            num='5.0'
            letter='-'
        elif grade=='V?':
            num=np.nan
            letter=''
        elif grade[0]=='5':
            for val in ('a','b','c','d','+','-', 'a/b','b/c','c/d'):
                if val in grade:
                    num=grade[:grade.index(val)]
                    letter=val
        elif grade[:2] in ('WI', 'AI'):
            if 'M' in grade:
                first=grade[:grade.index(' ')]
                num1, letter1=dealwithplusminus(first)
                sec=grade[grade.index(' ')+1:]
                num2, letter2=dealwithplusminus(sec)
                num='%s %s' %(num1, num2)
                letter='%s %s' %(letter1, letter2)
            else:
                num, letter=dealwithplusminus(grade)
        elif grade[0] in ('V','C','A', 'M'):
            if "easy" in grade:
                num='V0'
                letter='-'
            else:
                num, letter=dealwithplusminus(grade)
        if output=='num':
            return num
        elif output=='letter':
            return letter
    else:
        return None
        
def dealwithplusminus(grade):
    if grade[-1]=='-':
        num=grade[:grade.index('-')]
        letter=grade[-1]
    elif '-' in grade:
        num=grade[:grade.index('-')]
        letter='+'
    elif '+' in grade:
        num=grade[:grade.index('+')]
        letter=grade[-1]
    else:
        num=grade
        letter=''
    return num, letter