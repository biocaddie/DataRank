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
        precision=[]
        for i in range(len(results)):
            precision.append((i+1)/results[i])
        return np.mean(precision)
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
def eval_multiclass(ranking,k=-1):
    MRRs,APs=[],[]
    for target, row in ranking.iterrows():
        APs.append( AP(row.values, [target],k=k)) 
        MRRs.append(MRR( row.values, [target],k=k))
    return MRRs,APs
    
def eval_mesh():
    path='/home/arya/PubMed/GEO/Datasets/libsvm/out/'
    dspath='/home/arya/libsvm/glass'
    import os , pickle,sys
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.svm import libsvm, LinearSVC,libsvm_sparse,SVC
    from sklearn.datasets import load_svmlight_file
    import numpy as np
    from time import time
    import pandas as pd
    for i in range(5):
        ranking=pd.read_pickle(path+'ranking.{}.df'.format(i))
        ranking.columns=ranking.columns.values.astype(int)
        ranking.index=ranking.index.values.astype(int)
        ranking=ranking.loc[np.intersect1d(ranking.index.values,ranking.columns.values)]
        rr,ap=eval_multiclass(ranking)
        print rr
        print 'MAP:', np.mean(ap)
        print 'MRR:',np.mean(rr)
        break

def eval_geo():
    pass
if __name__ == '__main__':
    eval_mesh()
