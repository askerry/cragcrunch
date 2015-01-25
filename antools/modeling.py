__author__ = 'amyskerry'

import numpy as np
import pandas as pd
import sklearn.metrics
import sklearn.preprocessing
import pickle
import os
from sklearn.cluster import KMeans, AffinityPropagation

import utilities as uf
import scipy.stats

from sklearn.grid_search import GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LinearRegression,LogisticRegression, Lasso, Ridge, ElasticNet
from sklearn.svm import SVC, SVR
from sklearn.ensemble import RandomForestClassifier

class RandomForestClassifierWithCoef(RandomForestClassifier):
    '''extension of the RandomForectClassifier class that allows me to call coef_ instead of feature_importances_ (for ease/consistency with APIs of other models)'''
    def fit(self, *args, **kwargs):
        super(RandomForestClassifierWithCoef, self).fit(*args, **kwargs)
        self.coef_ = self.feature_importances_
        
def classifier(clfname):
    if clfname=='gnb':
        clf=GaussianNB() #.sigma_ .theta_
    elif clfname=='rfc':
        clf=RandomForestClassifierWithCoef(n_estimators=10, oob_score=True)
    elif clfname=='svm':
        clf=SVC(kernel='linear', probability=True, C=1)
    elif clfname=='logistic':
        clf=LogisticRegression(C=1)
    return clf
    
def regression(clfname):
    if clfname=='ols':
        clf=LinearRegression(normalize=True)
    elif clfname=='ridge':
        clf=Ridge() 
    elif clfname=='lasso':
        clf=Lasso()
    elif clfname=='elastic':
        clf=ElasticNet()
    elif clfname=='svr':
        clf=SVR(kernel=kernel, C=Cparam)
    return clf




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


def cluster(df, colname, clustertype='kmeans', k=10):
    matrix=df.values
    labels=df[colname].values
    if clustertype=='affinity':
        clf=AffinityPropagation()
    elif clustertype=="kmeans":
        clf=KMeans(n_clusters=k)
    clusters=clf.fit_predict(matrix)
    return pd.DataFrame(data={colname:labels,'cluster':clusters})

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
    hitmat['climbid']=climbs
    return hitmat
    
def computestarmatrix(allclimbs, allclimbers,sdf):
    '''make climb x climber matrix filled in with star ratings'''
    climbs=[val for val in sdf.climb.unique() if val in allclimbs]
    climbers=[val for val in sdf.climber.unique() if val in allclimbers]
    mat=np.zeros([len(climbs), len(climbers)])
    mat[:,:] = np.nan
    sdf=sdf[(sdf['climb'].isin(climbs)) & (sdf['climber'].isin(climbers))]
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
    starmat['climbid']=climbs
    return starmat

def computeattributematrix(allclimbs, allcols, cdf):
    mat=cdf.loc[allclimbs,allcols].dropna()
    allclimbs=mat.index.values
    normalizer=sklearn.preprocessing.StandardScaler(copy=True, with_mean=True, with_std=True)
    nmat=normalizer.fit_transform(mat.values)
    attrmat=pd.DataFrame(index=allclimbs, columns=allcols, data=nmat)
    attrmat['climbid']=allclimbs
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
    del locdf['area']
    return locdf.dropna()

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

def getuserratings(sdf, cdf, u, features, truecol):
    '''return X matrix of features, Y array of labels, list of climb indices'''
    includedclimbs=[val for val in sdf[(sdf['climber']==u) & sdf['starsscore']>0]['climb'].values if val in cdf.index.values] #all star ratings provided by user
    climbdf=cdf.loc[includedclimbs,:]
    climbids=climbdf['climbid'].values
    selectedclimbscores=sdf[sdf['climber']==u].groupby('climb').mean()
    Y=selectedclimbscores.loc[climbids,truecol].values #true rating
    X=cdf.loc[climbids,features].values #training features are word counts
    return X, Y, climbids
    
def getuserspecificfeatures(user, sdf, climbs, featname):
    sdf=sdf[sdf['climber']==user].groupby('climb').mean().loc[climbs,:]
    featvec=sdf[featname].values
    return featvec.reshape(len(featvec),1)


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
    
    
def classify(clf,users, sfeatures,cfeatures, cdf, sdf, minratings=10, dropself=False, truecol='starsscore', datadir=None, getfeats=False):
    summary={'score':[], 'user':[], 'ntest':[]}
    results={'user':[],'climbid':[],'true_rating':[], 'feat_pred':[]}
    importantfeats=[]
    try:
        features=[float(x) for x in cfeatures]
    except:
        features=[x for x in cfeatures]
    climbers=[]
    for u in users:
        if dropself and u in [str(f) for f in features]:
            features.remove(u)
        X, Y, climbs=getuserratings(sdf, cdf, u, cfeatures, truecol)
        for s in sfeatures:
            featvec=getuserspecificfeatures(u, sdf, climbs, s)
            X=np.hstack([X,featvec])
            features.append(s)
        print features
        if len(climbs)>minratings:
            climbers.append(u)
            folds=sklearn.cross_validation.LeaveOneOut(len(climbs))
            userfeats=[]
            for train_i, test_i in folds:
                results, summary, feats=foldresult(X,Y,train_i, test_i, clf, summary, results, climbs, u, features, getfeats)
                userfeats.extend(list(feats))
            userfeats=[str(word) for word in userfeats if not uf.isfloatable(str(word))]
            importantfeats.append(userfeats)
            if datadir is not None:
                clf.fit(X, Y)
                finalclf=savefinalmodel(X,Y,clf,u,features,datadir)
    importantfeats=makefeatdf(importantfeats, climbers)
    resultsdf=pd.DataFrame(data=results)    
    summarydf=pd.DataFrame(data=summary) 
    return summarydf, resultsdf, importantfeats  

def makefeatdf(importantfeats, climbers):
    allrelfeats=set([word for row in importantfeats for word in row])
    featcounts={}
    for feat in allrelfeats:
        featcounts[feat]=[float(row.count(feat))/len(row) for row in importantfeats]
    df=pd.DataFrame(data=featcounts)
    df['climber']=climbers
    return df

def gettval(array):
    t,p=scipy.stats.ttest_1samp(array, 0)
    return [t,p]
    
def foldresult(X,Y,train_i, test_i, clf, summary, results, climbs, u, features, getfeats):
    X_train,X_test, Y_train, Y_test = X[train_i], X[test_i], Y[train_i], Y[test_i]
    normalizer=sklearn.preprocessing.StandardScaler(copy=True, with_mean=True, with_std=True)
    X_train=normalizer.fit_transform(X_train)
    X_test=normalizer.transform(X_test)
    importantfeats=[]
    if len(set(Y_train))>1:
        clf.fit(X_train, Y_train)
        ypred=clf.predict(X_test)
        score=clf.score(X_test, Y_test)
        summary=addsummary(summary, score, Y_test, u)
        for inum,i in enumerate(test_i):
            results=addresult(i,inum, results, climbs, Y_test, ypred, u)
        if getfeats:
            importantfeats=getfeatimportances(clf, np.array(features), 10)
        else:
            importantfeats=[]
    return results, summary, importantfeats
    
def getfeatimportances(clf,features, k):
    coefs=clf.coef_
    feats=features[np.argsort(coefs)]
    return feats[-k:]
    
def savefinalmodel(X,Y,clf,u,features,datadir):
    clf.fit(X, Y)
    finalclf={'user':u, 'clf':clf, 'features':features}
    fname='models/user_%s_model.pkl'%(u)
    filename=os.path.join(datadir,fname)  
    with open(filename, 'wb') as output:
        pickler = pickle.Pickler(output, pickle.HIGHEST_PROTOCOL)
        try:
            pickler.dump(finalclf)
        except:
            print "pickle fail"
    return finalclf
    