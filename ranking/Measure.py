'''
Created on Jul 3, 2015

@author: arya
'''
import pandas as pd
import numpy as np
import pickle as pk
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
def evalMulticlass(ranking,k=-1):
    MRRs,APs=[],[]
    for target, row in ranking.iterrows():
        APs.append( AP(row.values, [target],k=k)) 
        MRRs.append(MRR( row.values, [target],k=k))
    return MRRs,APs

def evalMultilabel(ranking, labels, DP,k=-1):
    MRRs,APs=[],[]
    for (_,row), (_, lab) in zip(ranking.iterrows(), labels.iterrows()):
        target= DP.loc[labels.columns[lab.values.astype(bool)]].accession.values
        result=DP.loc[row.values].accession.values
        APs.append( AP(result, target,k=k)) 
        MRRs.append(MRR( result, target,k=k))
    return MRRs,APs


def sigmoid(z):
    return  1.0 / (1.0 + np.exp(-1.0 * z))

def evalMeSHSVM(theta=1):
    path='/home/arya/PubMed/GEO/Datasets/libsvm/out/'
    DP=pd.read_pickle('/home/arya/PubMed/GEO/Datasets/DPP.df')[['accession','pmid']].drop_duplicates()
    DP.index=DP.pmid.astype(int)
    imp=np.log(pd.read_pickle('/home/arya/PubMed/GEO/Datasets/importance.df'))
    imp=pd.merge(DP,imp,left_on='accession',right_index=True)
    imp["idx"] = imp.index
    imp=imp.drop_duplicates(cols='idx').cc
    imp
    MRR,MAP=[],[]
    MRRI,MAPI=[],[]
    for i in range(5):
        print i
        deci,labels=pd.read_pickle(path+'deci.{}.multilabel.df'.format(i)), pd.read_pickle(path+'labels.{}.multilabel.df'.format(i))
        ranking= pd.DataFrame(columns=range(1,deci.shape[1]+1),data=deci.columns[deci.values.argsort()[:,::-1]])
        rr,ap=evalMultilabel(ranking,labels,DP)
        MAP.append( np.mean(ap));        MRR.append(np.mean(rr))
        decImp=deci.values + theta*imp.loc[deci.columns].values[None,:]
        ranking= pd.DataFrame(columns=range(1,deci.shape[1]+1),data=deci.columns[decImp.argsort()[:,::-1]])
        rr,ap=evalMultilabel(ranking,labels,DP)
        MAPI.append( np.mean(ap));        MRRI.append(np.mean(rr))
    print MAP,MAPI
    print MRR,MRRI
    pk.dump({'SVM':MAP,'SVMI':MAPI}, open(path+'MAP.pkl','wb'))
    pk.dump({'SVM':MRR,'SVMI':MRRI}, open(path+'MRR.pkl','wb'))
    
def eval_geo():
    path='/home/arya/PubMed/GEO/Datasets/MeSH.Query.resultss'
    
    q=pd.read_pickle('/home/arya/PubMed/GEO/Datasets/Query.MeSH.df')
    lines=open(path).readlines()
    len(lines)
    res=pd.DataFrame(map(lambda x: (x.strip().split(',')[0], x.strip().split(',')[1:]), lines))
    res
    
    
#     pk.dump(path, open(path+'MAP.GEO.pkl','wb'))
#     pk.dump(path, open(path+'MRR.GEO.pkl','wb'))

if __name__ == '__main__':
    evalMeSHSVM()
    print 'Done'
