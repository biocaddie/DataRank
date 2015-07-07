'''
Created on Jul 3, 2015

@author: arya
'''
import pandas as pd
import numpy as np
def AP(ranking, targets,k=-1):
    if k>0:
        ranking=ranking[:k]
    """average precision"""
    ranking=np.array(ranking)
    results=np.array([])
    for tt in targets:
        results =np.append(results, np.where(ranking==tt)[0])
    results +=1
    if len(results):
        return  len(results)/float(len(ranking))
    else:
        return 0
        

def MRR(ranking, targets,k=-1):
    """mean reciprocal rank"""
    """average precision"""
    if k>0:
        ranking=ranking[:k]
    ranking=np.array(ranking)
    results=np.array([])
    for tt in targets:
        results =np.append(results, np.where(ranking==tt)[0])
    if len(results):
        results +=1
        return  1.0/min(results)
    else:
        return 0
def eval_multiclass(ranking):
    MRRs,APs=[],[]
    for target, row in ranking.iterrows():
        APs.append( AP(row.values, [target])) 
        MRRs.append(MRR( row.values, [target]))
    return MRRs,APs
    
    
def eval_mesh(path='/home/arya/PubMed/GEO/Datasets/'):
    dspath='/home/arya/libsvm/glass'
    import os , pickle,sys
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.svm import libsvm, LinearSVC,libsvm_sparse,SVC
    from sklearn.datasets import load_svmlight_file
    import numpy as np
    from time import time
    import pandas as pd
    X, y = load_svmlight_file(dspath)
    model=OneVsRestClassifier(LinearSVC(random_state=0)).fit(X, y)
    deci=model.decision_function(X)
    labels=model.classes_
    ranking= pd.DataFrame(columns=labels,data=labels[deci.argsort()[:,::-1]])
    deci=pd.DataFrame(columns=labels,data=deci)
    ranking.index,deci.index=y,y
    ranking.index.name,deci.index.name='y','y'
    pred=model.predict(X)
    ranking=pd.read_pickle(path+'ranking.0.df')
    ranking=ranking.loc[np.intersect1d(ranking.index.values,ranking.columns.values)]
    mrr,map=eval_multiclass(ranking)
    print 'MAP:'; np.sum(map)
    print 'MRR:',np.sum(mrr)

if __name__ == '__main__':
    eval_mesh()
