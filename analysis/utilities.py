# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 10:11:44 2015

@author: amyskerry
"""

import clean


def cleandf(df):
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
    return df
    
def reindex(df):
    for col in df.columns:
        if col in ('climbid', 'areaid', 'climberid', 'ticksid', 'commentsid', 'gradesid', 'starid', 'todosid'):
            df.index=[int(val) for val in df[col].values]
    return df