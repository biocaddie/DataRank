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
        dspath='{}libsvm/train.{}{}.libsvm'.format(path,fold, ('','.multilabel')[multilabel])
        start=time()
        warnings.filterwarnings('ignore')
        X, y = load_svmlight_file(dspath,multilabel=multilabel)
        runname='.{}{}'.format(fold,('','.multilabel')[multilabel])
        print 'learning...', sys.stdout.flush()
        model=OneVsRestClassifier(LinearSVC(random_state=0)).fit(X, y)
        X, y = load_svmlight_file(dspath.replace('train','test'),multilabel=True)
        print 'predicting...', sys.stdout.flush()
        deci=model.decision_function(X)
        labels=model.classes_
        ranking= pd.DataFrame(columns=labels,data=labels[deci.argsort()[:,::-1]])
        deci=pd.DataFrame(columns=labels,data=deci)
        if multilabel:
            (pd.DataFrame(columns=labels,data=MultiLabelBinarizer().fit_transform(y))).to_pickle('{}labels{}.df'.format(outpath,runname))
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
#     compute_ranking(multilabel=True)
    compute_ranking()
    print 'Done'
