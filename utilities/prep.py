# -*- coding: utf-8 -*-
"""
Created on Wed May 27 19:41:31 2015

@author: amyskerry
"""
import numpy as np
import nltk
from collections import Counter, OrderedDict
import json
import sys
import retrieval
import collections
import sys, os
rootdir=os.getcwd()
while 'Projects' in rootdir:
    rootdir=os.path.dirname(rootdir)
sys.path.append(os.path.join(rootdir, 'Projects', 'credentials'))
from sqlcfg import projectroot 
fulldir=rootdir+projectroot
print fulldir

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
    
def hacks(string):
    '''I have some very specific hacks I want to implement instead of standard stemming'''
    misc_hacks={'bouldery':'boulder','crimpy':'crimp', 'juggy':'jug','slabby':'slab','overhang':'overhung', 'pumpy':'pump','hang':'hung'}
    for word in misc_hacks.keys():
        if word in string:
            string=string.replace(word,misc_hacks[word])
    return string
    
def nanify(val, nanvalues=('','None','unavailable', None)):
    if val in nanvalues:
        return np.nan
    return val
    
################################
#          Miscellaneous       #
################################
    
def rating_confidence(climbid, sdf=None):
    '''return number of people who have rated a climb, and the std of ratings'''
    if sdf is not None:
        relevants=sdf[sdf['climb']==climbid]['starsscore'].values
    else:
        relevants=retrieval.query_filter('stars', {'climbid':climbid}, 'starsscore')
    return len(relevants), np.std(relevants)
    
def load_text_feats(path=os.path.join(fulldir,'cfg/apriori.json')):
    with open(path, 'r') as f:
        j=f.read()
    return json.loads(j, object_pairs_hook=collections.OrderedDict) 
    
def text_processing(string, feature_dict):
    wordlist=nltk.tokenize.word_tokenize(string.lower())
    c=Counter()
    for term in feature_dict:
        for word in wordlist:
            if any([match==word[:len(match)] for match in feature_dict[term]]):
                c[term]+=1
    props=OrderedDict()
    for term in feature_dict:
        props[term]=float(c[term])/len(wordlist)
    return props.values()
                
    
    
################################
#        Grade Processing      #
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
    
################################
#      Reduction Checks        #
################################

def is_international(region, exclusions=('Africa', 'Europe', 'Australia', 'Oceania', 'Asia', 'South America')):
    return region in exclusions
    
def is_silly_style(stylestr, exclusions=('Alpine', 'Ice', 'Mixed', 'Chipped', 'Aid')):
    return stylestr in exclusions    
    
def is_graded(grade, style):
    if grade !='nan':
        if style in ['Sport', 'Trad', 'TR'] and grade.startswith('5'):
            return True
        elif style =='Boulder' and grade.startswith('V'):
            return True
    return False
    
    
################################
#       Area Processing        #
################################  
    
def getregion(mid, areadf): ### needs to be a db access
    return areadf[areadf['areaid']==mid].region.values[0]
    
def check_one_level_down(areaid, othermains, areadf=None):
    if areadf is not None:
        top_views=areadf[areadf['areaid']==areaid].iloc[0]['pageviews']
        lowers=areadf.loc[areadf['area']==areaid]
        lowerids, lowerviews=lowers['areaid'].values, lowers['pageviews'].values
    else:
        top_views=retrieval.query_filter('area', {'areaid':areaid}, 'starscore')[0]
        lowerids, lowerviews=retrieval.get_pageviews(areaid)
    for lowerid, lowerview in zip(lowerids, lowerviews):
        if lowerview>top_views:
            othermains.append(lowerid)
    return othermains
    
def find_state_and_main(areaid, stateids=None, areadf=None):
    if areadf is not None:
        higher_areaid=areadf.loc['areaid'==areaid,'area']#
    else:
        higher_areaid=retrieval.get_area(areaid)
    if higher_areaid not in stateids:
        return find_state_and_main(higher_areaid, stateids=stateids, areadf=areadf)
    else:
        return higher_areaid, areaid
        
def getsubareas(areaid, areadf=None):### needs to be a db access
    '''get children areas'''
    if areadf is not None:
        subareaids=list(areadf.loc[areadf['area']==areaid, 'areaid'].values)
    else:        
        subareaids=list(retrieval.query_filter('area', {'area':areaid}, 'areaid'))
    for area in subareaids:
        subareaids.extend(getsubareas(area, areadf=areadf))
    return subareaids