'''
Created on Jul 9, 2015

@author: arya
'''
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle as pk
path='/home/arya/PubMed/'
def plot(y,MAP=True,fontsize=30,figsize=(18, 10), dpi=80):
    plt.figure(figsize=figsize, dpi=dpi)
    mpl.rc('font', **{'family': 'serif', 'serif': ['Times'], 'size':fontsize})
#     mpl.rc('text', usetex=True)
    
    x = range(3)
    m =y.mean( axis=1)
    print m
    title=["MRR","MAP"][MAP]
    labels = ['GEO', 'Only Relevance', 'Relevance\nand Importance']
    error=y.std(axis=1)/2
    plt.errorbar(x,m, yerr=error, fmt='ok',linewidth=2, markersize=15)
    plt.xlim([-1,3])
    plt.ylim([-0.01,max(m)+max(error)+0.05])
    plt.grid()
    plt.xticks(x, labels)
    plt.title(title)
    plt.savefig(path+title+'.png')
    plt.show()
    

if __name__ == '__main__':
    y=pk.load(open(path+'MRR.pkl'))
    plot(y,MAP=False)
    y=pk.load(open(path+'MAP.pkl'))
    plot(y,MAP=True)
    