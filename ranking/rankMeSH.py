'''
Created on Jun 26, 2015

@author: arya
'''
import subprocess
import os
import cmd
from svmutil import *
def learn_svm(ds='/home/arya/libsvm/wine', C=10, G=1, cv=0, runnrame='foo' , linear=True, exe='/home/arya/libsvm/svm-train', out='/home/arya/out/'):
    if not os.path.exists(out):            os.makedirs(out)
    cmd='{} -c {} -t {} {} {} {}model '.format(exe, C, ( '{} -g {}'.format(2,1), 0)[linear], ('' ,'-v {}'.format(cv))[cv>0], ds, out)
    print cmd
    proc= subprocess.Popen(cmd, shell= True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cv:
        print cv, 'Fold', proc.stdout.readlines()[-1].strip() 

def learn_svm2(ds='/home/arya/libsvm/wine', C=10, G=1, cv=0, runnrame='foo' , linear=True, exe='/home/arya/libsvm/svm-train', out='/home/arya/out/'):
    y, x = svm_read_problem(ds)
    m = svm_train(y, x, '-c 4')
    p_label, p_acc, p_val = svm_predict(y, x, m)
    print m.label
    print p_label,
    print p_val
    print len(p_val)
     
def predict_svm(ds='/home/arya/libsvm/wine', exe='/home/arya/libsvm/svm-predict', out='/home/arya/out/'):
    if not os.path.exists(out):            os.makedirs(out)
    cmd='{} {} {}model {}predict '.format(exe, ds, out,out)
    print cmd
    proc= subprocess.Popen(cmd, shell= True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == '__main__':
    learn_svm2()
#     predict_svm() 
