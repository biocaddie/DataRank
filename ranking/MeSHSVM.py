'''
Created on Jun 26, 2015

@author: arya
'''
import subprocess
import os , pickle,sys
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import libsvm, LinearSVC,libsvm_sparse,SVC
from sklearn.datasets import load_svmlight_file
import numpy as np
from time import time
import pandas as pd
import scipy.sparse as sps

from sklearn.preprocessing import  MultiLabelBinarizer 

def correct_dataset(path):
    lines=open(path).readlines()
    with open(path,'w') as f:
        for line in lines:
            print >> f,line.replace(', ', ',').strip()
def correct_all():            
    path='/home/arya/PubMed/GEO/Datasets/'
    multilabel=True
    for fold in range(5):
        dspath='{}libsvm/train.{}.{}.libsvm'.format(path,fold, ('multiclass','multilabel')[multilabel])
        correct_dataset(dspath)
        correct_dataset(dspath.replace('train', 'test'))
        
def remove_unknown_classes(y, labels):        
    len(y)
    labels.shape
    new_y=[]
    for i in range(len( y)):
        sample_y=[]
        for l in y[i]:
            if l in labels:
                sample_y.append(l)
        new_y.append(sample_y)
    return new_y    
        
    
def compute_ranking(nr_folds=5,multilabel=False):
    path='/home/arya/PubMed/GEO/Datasets/'
    outpath='{}libsvm/out/'.format(path)
    stdout_old=sys.stdout
    stderr_old=sys.stderr
    sys.stdout=open('{}MeSH{}.log'.format('/home/arya/PubMed/GEO/Log/',('.multiclass','.multilabel')[multilabel]),'w')
    sys.stderr=open('{}MeSH{}.err'.format('/home/arya/PubMed/GEO/Log/',('.multiclass','.multilabel')[multilabel]),'w')
    if not os.path.exists(outpath):            os.makedirs(outpath)
    for fold in range(nr_folds):
        import warnings
        dspath='{}libsvm/train.{}.{}.libsvm'.format(path,fold, ('multiclass','multilabel')[multilabel])
        start=time()
        warnings.filterwarnings('ignore')
        print 'loading', dspath
        X, y = load_svmlight_file(dspath,multilabel=multilabel)
        runname='.{}{}'.format(fold,('.multiclass','.multilabel')[multilabel])
        print 'learning...',runname,X.shape,  sys.stdout.flush()
        model=OneVsRestClassifier(LinearSVC(random_state=0)).fit(X, y)
        print 'loading', dspath
        X, y = load_svmlight_file(dspath.replace('train','test'),multilabel=multilabel)
        labels=model.classes_
        X=sps.csr_matrix((X.data, X.indices, X.indptr), shape=(X.shape[0], 27456))
        if multilabel:
            y=remove_unknown_classes(y, labels)
            idx=np.array(map(lambda x: len(x)>0,y))
            y=np.array(y)[idx]
            X=X[idx]
        print 'predicting...',('multiclass','multilabel')[multilabel],X.shape, sys.stdout.flush()
        deci=model.decision_function(X)
        
        ranking= pd.DataFrame(columns=labels,data=labels[deci.argsort()[:,::-1]])
        deci=pd.DataFrame(columns=labels,data=deci)
        if multilabel:
            (pd.DataFrame(columns=labels,data=MultiLabelBinarizer().fit_transform(list(y)+[labels]))).iloc[:-1].to_pickle('{}labels{}.df'.format(outpath,runname))
        else:
            ranking.index,deci.index=y,y
            ranking.index.name,deci.index.name='y','y'
            pred=model.predict(X)
            print 'Accuracy:', np.mean(y==pred)
        ranking.to_pickle('{}ranking{}.df'.format(outpath,runname))
        deci.to_pickle('{}deci{}.df'.format(outpath,runname))
        print 'Done in {:.0f} minutes'.format((time()-start)/60.0)
    sys.stderr=stderr_old
    sys.stdout=stdout_old

if __name__ == '__main__':
#     compute_ranking(multilabel=False)
    compute_ranking(multilabel=True)

    print 'Done'
