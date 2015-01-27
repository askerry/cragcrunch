# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 11:43:42 2015

@author: amyskerry
"""
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer


    
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

def makedescripdf2(df, terms, columns):
    '''take set of terms and count occurrences of each in each row of dataframe'''
    ddf=df.copy()
    for c in columns:
        for t in terms:
            ddf["%s_%s" %(t,c)]=df[c].apply(countterm, term=t) #using this simple approach to tokenization/vectorizing because I'm using a hand selected set of words and multiword phrases and don't have to worry about word subset issues
    return ddf
    
def makedescripdf(df, terms, columns):
    '''take set of terms and count occurrences of each in each row of dataframe'''
    ddf=df.copy()
    for c in columns:
        indices=df[c].dropna().index.values
        listofstrings=df[c].dropna().values
        listofstrings=[hacks(string) for string in listofstrings]
        vectorizer = CountVectorizer(input=listofstrings, vocabulary=terms)
        wordcounts = vectorizer.fit_transform(listofstrings)
        wordcounts=wordcounts.toarray()
        featurenames = vectorizer.get_feature_names()
        for tn,t in enumerate(featurenames):
            ddf["%s_%s" %(t,c)]=np.nan
            ddf.loc[indices, "%s_%s" %(t,c)]=wordcounts[:,tn] 
    return ddf   

def hacks(string):
    '''I have some very specific hacks I want to implement instead of standard stemming'''
    twogramfeats=['flaring crack','fingers crack', 'wide crack','thin crack', 'no pro']
    misc_hacks={'bouldery':'boulder','crimpy':'crimp', 'juggy':'jug','slabby':'slab','overhang':'overhung', 'pumpy':'pump','hang':'hung'}
    for f in twogramfeats:
        if f in string:
            fsquash=''.join(f.split(' '))
            string=string.replace(f,fsquash)
    for word in misc_hacks.keys():
        if word in string:
            string=string.replace(word,misc_hacks[word])
    return string
    
        
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
    

    