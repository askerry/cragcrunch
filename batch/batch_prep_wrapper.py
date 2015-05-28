# -*- coding: utf-8 -*-
"""
Created on Wed May 27 20:19:21 2015

@author: amyskerry
"""
import numpy as np

def cleandf(df):
    '''apply various functions to clean string inputs from html'''
    nanvalues=['','None','unavailable', None]
    df=df.applymap(lambda x:np.nan if x in nanvalues else x)
    for col in df.columns:
        if col in ('climbid', 'areaid', 'climberid', 'ticksid', 'commentsid', 'gradesid', 'starid', 'todosid', 'climb', 'climber', 'area'):
            df[col]=df[col].convert_objects(convert_numeric=True).values
        elif col in ('starsscore', 'age', 'avgstars'):
            df[col]=df[col].convert_objects(convert_numeric=True).values
        elif col =='pageviews':
            df[col]=df[col].apply(clean.removecomma)
        elif col=='maplocation':
            df['latitude']=df[col].apply(clean.getlat)
            df['longitude']=df[col].apply(clean.getlong)
            del df['maplocation']
        elif col in ('elevation', 'length'):
            df[col]=df[col].apply(clean.striplength)
        elif col=='pitch':
            df[col]=df[col].apply(clean.pitch)
        else:
            df[col]=df[col].apply(clean.strip)
        if col=='url':
            df['urlname']=df[col].apply(clean.extractname)
        if col=='style':
            df[col]=df[col].apply(clean.mergeiceandsnow)
        if col =='pitch':
            df[col]=df[col].apply(clean.strippitch)

    return df