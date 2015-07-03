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

from sklearn.preprocessing import  MultiLabelBinarizer 

def get_ranking(fold=0):
    path='/home/arya/PubMed/GEO/Datasets/'
    C=1
    import warnings
    outpath='{}libsvm/out/'.format(path)
    if not os.path.exists(outpath):            os.makedirs(outpath)
    dspath='{}libsvm/train.{}.libsvm'.format(path,fold)
    start=time()
    warnings.filterwarnings('ignore')
    X, y = load_svmlight_file(dspath)
    runname='.{}'.format(fold)
    stdout_old=sys.stdout
    stderr_old=sys.stderr
    sys.stdout=open('{}model{}.log'.format(outpath,runname),'w')
    sys.stderr=open('{}model{}.err'.format(outpath,runname),'w')
    model=OneVsRestClassifier(LinearSVC(random_state=0,C=C)).fit(X, y)
    print 'learning...'
    X, y = load_svmlight_file(dspath.replace('.train','.test'))
    print 'predicting...'
    deci=model.decision_function(X)
    pred=model.predict(X)
    labels=model.classes_
    ranking= labels[deci.argsort()[:,::-1]]
    ranking= pd.DataFrame(index=y,columns=labels,data=ranking)
    ranking.index.name='y'
    ranking.to_pickle('{}ranking{}.df'.format(outpath,runname))
    deci=pd.DataFrame(index=y,columns=labels,data=deci)
    deci.index.name='y'
    print 'Accuracy:', np.mean(y==pred)
    deci.to_pickle('{}deci{}.df'.format(outpath,runname))
    print 'Done in {:.0f} minutes'.format((time()-start)/60.0)
    sys.stderr=stderr_old
    sys.stdout=stdout_old

def get_ranking_multilabel(fold=0):
    path='/home/arya/PubMed/GEO/Datasets/'
    C=1
    import warnings
    outpath='{}libsvm/out/'.format(path)
    if not os.path.exists(outpath):            os.makedirs(outpath)
    dspath='{}libsvm/train.{}.libsvm'.format(path,fold)
    dspath='/home/arya/libsvm/yeast'
    start=time()
    warnings.filterwarnings('ignore')
    X, y = load_svmlight_file(dspath,multilabel=True)
    runname='.{}.multilabel'.format(fold)
    stdout_old=sys.stdout
    stderr_old=sys.stderr
    sys.stdout=open('{}model{}.log'.format(outpath,runname),'w')
    sys.stderr=open('{}model{}.err'.format(outpath,runname),'w')
    model=OneVsRestClassifier(LinearSVC(random_state=0,C=C)).fit(X, y)
    print 'learning...'
    X, y = load_svmlight_file(dspath.replace('.train','.test'),multilabel=True)
    print 'predicting...'
    
    deci=model.decision_function(X)
    pred=model.predict(X)
    labels=model.classes_
    ranking= labels[deci.argsort()[:,::-1]]
    ranking= pd.DataFrame(columns=labels,data=ranking)
    ranking.to_pickle('{}ranking{}.df'.format(outpath,runname))
    deci=pd.DataFrame(columns=labels,data=deci)
    
    BY= pd.DataFrame(columns=labels,data=MultiLabelBinarizer().fit_transform(y))
    BY.to_pickle('{}labels{}.df'.format(outpath,runname))
    print 'Accuracy:', np.mean(y==pred)
    deci.to_pickle('{}deci{}.df'.format(outpath,runname))
    print 'Done in {:.0f} minutes'.format((time()-start)/60.0)
    sys.stderr=stderr_old
    sys.stdout=stdout_old

if __name__ == '__main__':
    n_fold=5
    for fold in range(n_fold):
        get_ranking(fold)
#         get_ranking_multilabel(fold)
    print 'Done'
