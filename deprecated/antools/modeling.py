__author__ = 'amyskerry'

import numpy as np
import pandas as pd
import sklearn.metrics
import sklearn.preprocessing
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
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
        clf=RandomForestClassifierWithCoef(n_estimators=10, min_samples_split=2, max_features='sqrt', oob_score=True)
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

def gettopbottom_old(df, candidates, n=20):
    '''take similarity matrix and identify n most and least similar climbs'''
    candidates=[c for c in candidates if c in df.columns]
    df=df.loc[candidates,candidates]
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
    
def gettopbottom(simdf, climbid, allcandidates, n=10):
    '''take similarity matrix and identify n most and least similar climbs'''
    candidates=[c for c in allcandidates if c in simdf.columns]
    if len(candidates)<n*2 or climbid not in simdf.index.values:
        similar, dissimilar=[np.nan for x in range(n)],[np.nan for x in range(n)]
        for i in range(n):
            try:
                similar[i]=allcandidates[i]
                dissimilar[i]=allcandidates[-(i+1)]
            except:
                pass
        return similar, dissimilar
    row=simdf.loc[climbid,candidates]
    indices=list(np.argsort(row.values)) #sorted from nearest to furthest
    uind_near=np.array(indices[:n])
    uind_far=np.array(indices[-(n+1):])
    try:
        similar=np.array(candidates)[uind_near]
        dissimilar=np.array(candidates)[uind_far]
        return similar, dissimilar
    except:
        try:
            for i in range(n):
                try:
                    similar[i]=allcandidates[i]
                    dissimilar[i]=allcandidates[-(i+1)]
                except:
                    pass
            return similar, dissimilar
        except:
            return [np.nan for x in range(n)],[np.nan for x in range(n)]
    
def getsimilarclimbcandidates(climbid, cdf):
    numerizedgrade=cdf.loc[cdf['climbid']==climbid,'numerizedgrade'].values[0]
    if np.isnan(numerizedgrade):
        numerizedgrade=0
    style=cdf.loc[cdf['climbid']==climbid,'style'].values[0]
    if style=='TR':
        style='Sport'
    region=cdf.loc[cdf['climbid']==climbid,'region'].values[0]
    if style=='Boulder':
        graderange=[numerizedgrade-2, numerizedgrade+2]
    else:
        graderange=[numerizedgrade-3, numerizedgrade+3]
    if len(cdf)>20:
        cdf=cdf[cdf['region']==region]
    if len(cdf)>20:
        cdf=cdf[cdf['style']==style]
    if len(cdf)>20:
        tcdf=cdf[(cdf['numerizedgrade']<=graderange[1]) & (cdf['numerizedgrade']>=graderange[0])]
        if len(tcdf)<10:
            cdf=cdf[(cdf['numerizedgrade']<=graderange[1]+12) & (cdf['numerizedgrade']>=graderange[0]-12)]
        else:
            cdf=tcdf
    if len(cdf)>20:
        tcdf=cdf[cdf['avgstars']>=2]
        if len(tcdf)<10:
            cdf=cdf[cdf['avgstars']>=1]
        else:
            cdf=tcdf
    cdf=cdf[cdf['climbid']!=climbid]
    cdf=cdf.sort(columns=['avgstars','pageviews'], ascending=False)
    return cdf.climbid.values

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

def round2score(df, truecol, predcol, summary):
    preds=[np.round(x) for x in df[predcol].values]
    trues=df[truecol].values
    acc= sklearn.metrics.accuracy_score(trues,preds)
    precisiondf=df[df[predcol]==4] #TP/TP+FP
    precision=np.mean([precisiondf[predcol]==precisiondf[truecol]])
    recalldf=df[df[truecol]==4] #TP/TP+FN
    recall=np.mean([recalldf[predcol]==recalldf[truecol]])
    f1= 2 * (precision * recall) / (precision + recall)
    "**********Results for %s**********" %(predcol)
    print "4 way accuracy %.3f" %acc
    print "4 way f1 %.3f" %f1
    print "4 way precision %.3f" %precision
    print "4 way recall %.3f" %recall
    summary['f1'].append(f1)
    summary['acc'].append(acc)
    summary['precision'].append(precision)
    summary['recall'].append(recall)
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
def addresult(i, inum, results, climbs, Y_test, ypred, yprob, u):
    results['climbid'].append(climbs[i])
    results['true_rating'].append(Y_test[inum])
    results['feat_pred'].append(ypred[inum])
    results['prob'].append(yprob)
    results['user'].append(u)
    return results
    
    
def classify(clf,users, sfeatures,cfeatures, cdf, sdf, minratings=10, dropself=False, truecol='starsscore', datadir=None, getfeats=False):
    summary={'score':[], 'user':[], 'ntest':[]}
    results={'user':[],'climbid':[],'true_rating':[], 'feat_pred':[], 'prob':[]}
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
            if s not in features:
                features.append(s)
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
                finalclf=savefinalmodel(X,Y,clf,u,userfeats,datadir)
    importantfeats=makefeatdf(importantfeats, climbers)
    resultsdf=pd.DataFrame(data=results)    
    summarydf=pd.DataFrame(data=summary) 
    return summarydf, resultsdf, importantfeats, 

def makefeatdf(importantfeats, climbers):
    allrelfeats=set([word for row in importantfeats for word in row])
    featcounts={}
    for feat in allrelfeats:
        featcounts[feat]=[float(row.count(feat))/len(row) if len(row)>0 else 0 for row in importantfeats]
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
        yprobs=clf.predict_proba(X_test)[0]
        yprob=yprobs[-1]
        score=clf.score(X_test, Y_test)
        summary=addsummary(summary, score, Y_test, u)
        for inum,i in enumerate(test_i):
            results=addresult(i,inum, results, climbs, Y_test, ypred, yprob, u)
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
    
def regress(X,y):
    from sklearn.linear_model import LinearRegression
    clf= LinearRegression()
    clf.fit(X, y)
    R2=clf.score(X, y)
    predicted_y=clf.predict(X)
    residual_error=y-predicted_y
    return R2, residual_error, predicted_y

def iterativeregression(avgs, plotit=False, limit=None):
    features=avgs.columns
    keptfeatures,varexplained_full,varexplained_ind, iterationpredictions=[],[],[],[]
    initialdata=avgs[features].values
    y=avgs[features].values # y starts as initialdata and subsequently becomes the residuals
    if limit is None:
        limit=len(features)
    for i in range(limit):
        R2s=[]
        for f in range(len(features)): #regress each isolated feature against the data
            if f not in keptfeatures: #(if the feature has not already been selected)
                X = np.array([item[f] for item in initialdata]).reshape(len(y),1)
                R2, residual_error, predy = regress(X,y)
                R2s.append(R2)
            else:
                R2s.append(0)
        fn=R2s.index(np.max(R2s)) # best feature
        keptfeatures.append(fn)
        #recompute the relevant X vector and get its inidividual varexplained (in the fulldataset)
        keeperX = np.array([item[fn] for item in initialdata]).reshape(len(y),1)
        R2, residual_error, predy = regress(keeperX,initialdata)
        varexplained_ind.append(R2)
        #generate full X (of all kept features) to get the residuals
        fullX = np.array([item[keptfeatures] for item in initialdata])
        R2, residual_error, predy = regress(fullX,initialdata)
        iterationpredictions.append(predy)
        y = residual_error # the residuals are now our outcome variable for the subsequent iteration
        varexplained_full.append(R2)
    resultingfeatures=[features[fn] for fn in keptfeatures]
    print (', ').join(resultingfeatures)
    if plotit:
        f,ax=plt.subplots(2,1, figsize=[14,8])
        ax[0].plot(range(len(varexplained_full)), varexplained_full)
        ax[0].set_xlabel('features')
        ax[0].set_ylabel('total variance explained (cumulative)')
        ax[0].set_xticks(range(len(resultingfeatures)))
        ax[0].set_xticklabels(resultingfeatures, rotation=90)
        ax[1].plot(range(len(varexplained_ind)), varexplained_ind)
        ax[1].set_xlabel('features')
        ax[1].set_ylabel('individual feature R-squared')
        ax[1].set_xticks(range(len(resultingfeatures)))
        ax[1].set_xticklabels(resultingfeatures, rotation=90)
        plt.tight_layout()
        sns.despine()
    results={'df':avgs, 'predictions':iterationpredictions, 'features':resultingfeatures, 'varexp_full':varexplained_full, 'varexp_ind':varexplained_ind}
    return results
    
    