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
import multiprocessing

linear= not True

def get_ranking(split=0):
    path='/home/arya/PubMed/GEO/Datasets/'
    C=1
    
    import warnings
    outpath='{}libsvm/out/'.format(path)
    if not os.path.exists(outpath):            os.makedirs(outpath)
    dspath='{}libsvm/train.{}.libsvm'.format(path,split)
    start=time()
    warnings.filterwarnings('ignore')
    X, y = load_svmlight_file(dspath)
    runname='.{}.{}'.format(('Nonlinear','Linear')[linear],split)
    sys.stdout=open('{}model{}.log'.format(outpath,runname),'w')
    sys.stderr=open('{}model{}.err'.format(outpath,runname),'w')
    if linear:
        model=OneVsRestClassifier(LinearSVC(random_state=0,C=C)).fit(X, y)
    else:
        gamma=0.1
        model=OneVsRestClassifier(SVC(random_state=0,C=C, gamma=gamma)).fit(X, y)
#     pickle.dump(model,open('{}model{}.pkl'.format(outpath,runname),'wb'))
    print 'learning...'
    X, y = load_svmlight_file(dspath.replace('.train','.test'))
    print 'predicting...'
    deci=model.decision_function(X)
    pred=model.predict(X)
    labels=model.classes_
    ranking= labels[deci.argsort()[:,::-1]]
    print 'Accuracy:', np.mean(y==pred)
    pickle.dump({'deci':deci,'y':y, 'pred':pred},open('{}ranking{}.pkl'.format(outpath,runname),'wb'))
    print 'Done in {:.0f} minutes'.format((time()-start)/60.0)
    return ranking
    
if __name__ == '__main__':
    global linear
    linear=True
    numthreads=1
    print 'Training', ('Nonlinear','Linear')[linear]
    if numthreads==1:
        for split in range(10):
                get_ranking(split)
    else:
        pool=multiprocessing.Pool(numthreads)
        pool.map(get_ranking,range(10))
    linear=False
    print 'Done'
