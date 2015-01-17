# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 11:43:42 2015

@author: amyskerry
"""
import numpy as np

    
def mergeclimbcomment(commentdf, climbdf):
    '''merge all comments for climb into single string'''
    climbids=commentdf['climb'].unique()
    for c in climbids:
        comments=list(commentdf.loc[commentdf['climb']==c, 'comment'].values)
        commentsmerged='. '.join(comments)
        climbdf.loc[c,'commentsmerged']=commentsmerged
    return climbdf
    
    
# text processing
def countterm(string, term=None):
    '''count occurences of term in string'''
    try:
        return float(string.count(term))
    except:
        return np.nan

def makedescripdf(df, terms, columns):
    '''take set of terms and count occurrences of each in each row of dataframe'''
    ddf=df.copy()
    for c in columns:
        for t in terms:
            ddf["%s_%s" %(t,c)]=df[c].apply(countterm, term=t)
    return ddf
    
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
    

    