'''
Created on Jun 26, 2015

@author: arya
'''
import subprocess
import os , pickle
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import libsvm, LinearSVC,libsvm_sparse
from sklearn.datasets import load_svmlight_file
import numpy as np
from time import time



def get_ranking(path='/home/arya/PubMed/GEO/Datasets/',split=0,linear=True,C=1,gamma=0.1):
    import warnings
    outpath='{}libsvm/out/'.format(path)
    if not os.path.exists(outpath):            os.makedirs(outpath)
    dspath='{}libsvm/train.{}.libsvm'.format(path,split)
    start=time()
    warnings.filterwarnings('ignore')
    X, y = load_svmlight_file(dspath)
    if linear:
        model=OneVsRestClassifier(LinearSVC(random_state=0,C=C)).fit(X, y)
    else:
        model=OneVsRestClassifier(libsvm(random_state=0,C=C, gamma=gamma)).fit(X, y)
    pickle.dump(model,open('{}model_{}_C{}_G{}_{}.pkl'.format(outpath,('nonlinear','linear')[linear],C,gamma,split),'wb'))

    print 'learning...'
    X, y = load_svmlight_file(dspath.replace('.train','.test'))
    print 'predicting...'
    deci=model.decision_function(X)
    pred=model.predict(X)
    labels=model.classes_
    ranking= labels[deci.argsort()[:,::-1]]
    print 'Accuracy:', np.mean(y==pred)
    pickle.dump({'deci':deci,'y':y, 'pred':pred},open(outpath+'ranking.pkl','wb'))
    print 'Done in {:.0f} minutes'.format((time()-start)/60.0)
    return ranking
    
if __name__ == '__main__':
    get_ranking()
    