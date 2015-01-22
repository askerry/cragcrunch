__author__ = 'amyskerry'

import numpy as np
import pandas as pd
import sklearn.metrics

##################################################
#               Misc Model Setup                 #
##################################################

def splittraintest(df, climbids):
    ids=df[df['climb'].isin(climbids)].index.values
    test=df.copy()
    test=test.loc[ids,:]
    train=df.drop(ids)
    return test,train

##################################################
#             Similarity Functions               #
##################################################


def nansim(a,b,simmetric):
    import scipy.spatial.distance as ssd
    na,nb=dropnans(a,b)
    sim=ssd.pdist([na,nb],simmetric)
    return sim
def dropnans(a,b):
    a=a.astype(float)
    b=b.astype(float)
    zipped=zip(a,b)
    mask=np.array([~np.any(np.isnan(z)) for z in zipped])
    return a[mask],b[mask]  

def computepairwisesimilarity(x, df=None, similaritymetric='cosine'):
    row=x.values
    rowcorrs=[]
    for cn,c in df.iterrows():
        row2= c.values
        sim=nansim(row,row2,similaritymetric)
        rowcorrs.append(sim)
    values=[c[0] for c in rowcorrs]
    return values


def computeinteractionmatrix(allclimbs, allclimbers, hdf):
    '''make climb x climber matrix filled in with hits'''
    climbs=[val for val in hdf.climb.unique() if val in allclimbs]
    climbers=[val for val in hdf.climber.unique() if val in allclimbers]
    mat=np.zeros([len(climbs), len(climbers)])
    groups=hdf.groupby('climber').groups
    for g in groups.keys():
        climberindex=climbers.index(g)
        u_climbs=groups[g]
        for c in u_climbs:
            climb=hdf.loc[c,'climb']
            climbindex=climbs.index(climb)
            mat[climbindex,climberindex]=1
    hitmat=pd.DataFrame(index=climbs, columns=climbers, data=mat)
    return hitmat
    
def computestarmatrix(allclimbs, allclimbers,sdf):
    '''make climb x climber matrix filled in with star ratings'''
    climbs=[val for val in sdf.climb.unique() if val in allclimbs]
    climbers=[val for val in sdf.climber.unique() if val in allclimbers]
    mat=np.zeros([len(climbs), len(climbers)])
    mat[:,:] = np.nan
    groups=sdf.groupby('climber').groups
    for g in groups.keys():
        climberindex=climbers.index(g)
        u_climbs=groups[g]
        for c in u_climbs:
            rating=sdf.loc[c,'starsscore']
            climb=sdf.loc[c,'climb']
            climbindex=climbs.index(climb)
            mat[climbindex, climberindex]=rating
    starmat=pd.DataFrame(index=climbs, columns=climbers, data=mat)
    return starmat

def computeattributematrix(allclimbs, allcols, cdf):
    mat=cdf.loc[allclimbs,allcols].dropna()
    allclimbs=mat.climbid.values
    del mat['climbid']
    attrmat=pd.DataFrame(index=allclimbs, columns=allcols[1:], data=mat.values)
    return attrmat

def getcoord1up(adf,areaid):
    try:
        lon=adf[adf['areaid']==areaid].longitude.values[0]
        lat=adf[adf['areaid']==areaid].latitude.values[0]
    except:
        lon=np.nan
        lat=np.nan
    return lat,lon

def computelocationmatrix(cdf, adf, allclimbs):
    locdf=pd.merge(cdf,adf, left_on='area', right_on='areaid', how='inner')
    locdf['area']=locdf['area_x']
    locdf.index=locdf['climbid'].values
    allclimbs=[val for val in allclimbs if val in locdf.climbid.unique()]
    locdf=locdf.ix[allclimbs,:]
    locdf=locdf[['climbid','latitude', 'longitude','area']]
    for i in locdf[pd.isnull(locdf['latitude'])].index.values:
        aid=locdf.loc[i,'area']
        lat,lon=getcoord1up(adf,aid)
        if np.isnan(lat):
            aid=cdf.loc[i,'mainarea']
            lat,lon=getcoord1up(adf,aid)
        locdf.loc[i,'latitude']=lat
        locdf.loc[i,'longitude']=lon
    allclimbs=locdf['climbid']
    del locdf['climbid']
    del locdf['area']
    return pd.DataFrame(index=allclimbs, data=locdf.values).dropna()

def gettopbottom(df, n=20):
    '''take similarity matrix and identify n most and least similar climbs'''
    colnames=[str(val) for val in range(0,n+1)]
    colnames=colnames+['-'+str(val) for val in range(n,0,-1)]
    data={val:[] for val in colnames}
    for index, row in df.iterrows():
        indices=list(np.argsort(row.values)) #sorted from nearest to furthest
        uind=np.array(indices[:n]+indices[-(n+1):])
        selected=df.columns.values[uind]
        for cn,c in enumerate(colnames):
            data[c].append(selected[cn])
    data['climbid']=df.index.values
    return pd.DataFrame(index=df.index.values, data=data)

def getmatches(climbname, u_preddf, cdf, adf, arr):
    '''get info subset of climbs specified by <arr>'''
    ids=u_preddf.loc[cdf[cdf['name']==climbname].climbid,arr].values[0]
    climbs=cdf.loc[ids,:]
    climbnames=[cdf.loc[i,'name'] for i in ids]
    climbs['mainarea_name']=adf.loc[climbs.mainarea.values,'name'].values
    return climbs, climbnames

def getsimilar(climbname, u_preddf, cdf, adf):
    '''get names and dfs for similar and disimilar climbs'''
    simclimbs, simnames=getmatches(climbname, u_preddf, cdf, adf,['1','2','3','4','5', '6','7'])
    simclimbs=simclimbs[['name', 'mainarea', 'region', 'grade', 'description', 'style', 'mainarea_name']]
    dissimclimbs, dissimnames=getmatches(climbname, u_preddf, cdf, adf,['-1','-2','-3','-4','-5', '-6', '-7'])
    dissimclimbs=dissimclimbs[['name', 'mainarea', 'region', 'grade', 'description', 'style', 'mainarea_name']]
    return simclimbs, simnames, dissimclimbs, dissimnames

##################################################
#            Personalization Functions           #
##################################################

########################
#     Evaluation       #
########################

def round2score(df, truecol, predcol):
    preds=[np.round(x) for x in df[predcol].values]
    trues=df[truecol].values
    acc= sklearn.metrics.accuracy_score(trues,preds)
    f1=sklearn.metrics.f1_score(trues,preds, pos_label=4)
    precision=sklearn.metrics.precision_score(trues,preds, pos_label=4)
    recall=sklearn.metrics.recall_score(trues,preds, pos_label=4)
    "**********Results for %s**********" %(predcol)
    print "4 way accuracy %.3f" %acc
    print "4 way f1 %.3f" %f1
    print "4 way precision %.3f" %precision
    print "4 way recall %.3f" %recall
    return acc, precision, recall, f1
    
########################
#    Prep Prediction   #
########################
def normalizewordcounts(climbdf, features,key):
    '''replace word counts with word counts normalized by length of text'''
    climbs=climbdf['climbid'].values
    fullcontent=climbdf[key].values #len of description
    X=climbdf.loc[climbs,features].values #training features are word counts
    desclen=np.array([len(x) if isinstance(x,str) else 0 for x in fullcontent]) #get length of each description
    X=(X.T/desclen).T #normalize word counts by length of description
    climbdf.loc[climbs,features]=X
    return climbdf
def getuserratings(sdf, cdf, u, features):
    '''return X matrix of features, Y array of labels, list of climb indices'''
    climbs=[val for val in sdf[(sdf['climber']==u) & sdf['starsscore']>0]['climb'].values if val in cdf.index.values] #all star ratings provided by user
    climb_features=cdf.ix[climbs,:]
    climbs=climb_features['climbid'].values
    selectedclimbscores=sdf[sdf['climber']==u].groupby('climb').mean()
    Y=selectedclimbscores.ix[climbs,'starsscore'].values #true rating
    X=cdf.loc[climbs,features].values #training features are word counts
    return X, Y, climbs


########################
#    Run Prediction    #
########################    
def addsummary(summary, score, Y_test, u):
    summary['score'].append(score)
    summary['user'].append(u)
    summary['ntest'].append(len(Y_test))
    return summary
def addresult(i, inum, results, climbs, Y_test, ypred, u):
    results['climbid'].append(climbs[i])
    results['true_rating'].append(Y_test[inum])
    results['feat_pred'].append(ypred[inum])
    results['user'].append(u)
    return results
    
def classify(clf,users, features, cdf, sdf, minratings=10):
    summary={'score':[], 'user':[], 'ntest':[]}
    results={'user':[],'climbid':[],'true_rating':[], 'feat_pred':[], 'otheravg':[]}
    for u in users:
        X, Y, climbs=getuserratings(sdf, cdf, u, features)
        if len(climbs)>minratings:
            folds=sklearn.cross_validation.KFold(len(climbs), n_folds=len(climbs))
            for train_i, test_i in folds:
                X_train,X_test, Y_train, Y_test = X[train_i], X[test_i], Y[train_i], Y[test_i]
                if len(set(Y_train))>1:
                    clf.fit(X_train, Y_train)
                    ypred=clf.predict(X_test)
                    score=clf.score(X_test, Y_test)
                    summary=addsummary(summary, score, Y_test, u)
                    for inum,i in enumerate(test_i):
                        results=addresult(i,inum, results, climbs, Y_test, ypred, u)
    resultsdf=pd.DataFrame(data=results)    
    summarydf=pd.DataFrame(data=summary) 
    return summarydf, resultsdf  