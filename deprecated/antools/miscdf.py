# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 11:43:42 2015

@author: amyskerry
"""
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer
import pandas as pd


    
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
    for c in columns:
        for t in terms:
            df["%s_%s" %(t,c)]=df[c].apply(countterm, term=t) #using this simple approach to tokenization/vectorizing because I'm using a hand selected set of words and multiword phrases and don't have to worry about word subset issues
    return df

def mergestrs(str1, str2):
    if type(str1)==str and type(str2)==str:
        return str1+str2
    elif type(str1)==str:
        return str1
    elif type(str2)==str:
        return str2
    
def makedescripdf(df, terms):
    '''take set of terms and count occurrences of each in each row of dataframe'''
    ddf=df.copy()
    ddf=ddf[pd.notnull(ddf['mergedtext'])]
    listofstrings=ddf['mergedtext'].values
    listofstrings=[hacks(string) for string in listofstrings]
    vectorizer = CountVectorizer(input=listofstrings, vocabulary=terms)
    wordcounts = vectorizer.fit_transform(listofstrings)
    wordcounts=wordcounts.toarray()
    featurenames = vectorizer.get_feature_names()
    indices=ddf.index.values
    for tn,t in enumerate(featurenames):
        df["%s_description" %(t)]=0
        df.loc[indices, "%s_description" %(t)]=wordcounts[:,tn]     
    return df   

    
def maketextcomparedf(cdf):
    from nltk.corpus import movie_reviews
    negids = movie_reviews.fileids('neg')[:100]
    posids = movie_reviews.fileids('pos')[:100]
    ids=negids+posids
    listofstrings, kind, label=[],[],[]
    for i in ids:
        with movie_reviews.open(i) as f:
            listofstrings.append(f.read())
            kind.append('RT')
            if i[:3]=='pos':
                label.append(1)
            else:
                label.append(0)
    df=pd.DataFrame(data={'string':listofstrings, 'label':label, 'kind':kind}) 
    matchdf=cdf[[len(descrip)>1977 for descrip in cdf['description'].values]]
    label=matchdf['avgstars'].apply(lambda x:int(x>3.25))
    kind=['RC' for i in range(len(matchdf))]
    df2=pd.DataFrame(data={'string':matchdf['description'].values, 'label':label, 'kind':kind})
    return pd.concat([df,df2])
    