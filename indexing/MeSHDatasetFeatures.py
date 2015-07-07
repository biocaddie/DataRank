'''
Created on Jun 24, 2015

@author: arya
'''
import collections
import pandas as pd
import numpy as np
import sys,pickle,os
import pylab as plt
import collections
def clean_dic(dic):
    dic2={key: value  for (key, value) in dic.items() if value is not None and key is not None}
    return {key: value  for (key, value) in dic2.items() if len(value)}

def fix():
    path='/home/arya/PubMed/GEO/Datasets/'
    PP=pickle.load(open(path+'citations.pkl','rb'))
    PP= clean_dic(PP)
    redownload=[k for k,v in PP.items() if len(v[0])==2]
    
    print len(redownload),redownload[0]
    print PP[redownload[0]]
    for item in redownload:
        os.remove('/home/arya/PubMed/GEO/Citations/' +item+'.pkl')
        
    exit()
    print len(map(str.strip,open(path+'citations.log').readlines()))
    citations=list(set(map(str.strip,open(path+'citations.log').readlines())))
    print len(redownload)
    
    new_citations= [c for c in citations if c not in redownload]
    print len(new_citations)
    print len(citations)
    with open(path+'citations.log','w') as f:
        for c in new_citations:
            print >> f,c


def gse_dataset_stats(path='/home/arya/PubMed/GEO/Datasets/'):
    gse_pmid = pickle.load(open(path+'gse_pmid.pkl','rb'))
    gse_summary = pickle.load(open(path+'gse_summary.pkl','rb'))
    gse_title = pickle.load(open(path+'gse_title.pkl','rb'))
    print 'There are total of {} GEO Datasets which only\n{} has PMID\n{} has summary\n{} has title'.format( len((gse_pmid)), len(clean_dic(gse_pmid)), len(clean_dic(gse_summary)), len(clean_dic(gse_title)))

def gse_paper_stats(path='/home/arya/PubMed/GEO/Datasets/'):
    PP = (pickle.load(open(path+'citations.pkl','rb')))
    p=PP.keys()
    for _,v in clean_dic(PP).items():
        p+= v
    num_p=map(lambda (k,v):len(set(v)),clean_dic(PP).items())
    print 'So far, {} papers is pulled from WoS which are cited by {} papers ({} Uniques).'.format(len(PP),sum(num_p),len(set(p)))
    
    plt.hist(num_p,50,histtype='stepfilled')
    plt.xlabel('Number of Citaions')
    plt.ylabel('Papers')
    plt.show()
    
    PM = pickle.load(open(path+'PM.pkl','rb'))
    print 'There are {} papers which {} has MeSH terms.'.format(len(PM),len(clean_dic(PM)))
    PM=clean_dic(PM)
    num_mesh=map(lambda (k,v):len(set(v)),PM.items())
    plt.hist(num_mesh,20,histtype='stepfilled')
    plt.xlabel('Number of MeSH')
    plt.ylabel('Papers')
    plt.show()
    



def create_dataset(ppm):
    labels, feats=[],[]
    idx=ppm.index.unique()
    for i in idx:
        feat=np.append([27455],ppm.loc[i].mid.astype(int))
        label=ppm.loc[i].cited_pmid.astype(int)
        if  len(label.shape):
            label=label.unique()
        else:
            label=np.array([label])
        feats.append({k:1 for k in feat})
        labels.append( label)
    return labels,feats

def write_libsvm_dataset_multilabel(labels, feats,path):
    with open(path,'w') as f:
        for label,feat in zip(labels, feats):
            if len(label):
                line=', '.join(map(str,label)) 
                for k,v in sorted(feat.items(),key=lambda x: x[0]):
                    line+=' {}:{}'.format(k,v)
                print >>f,line

        
def create_MeSH_LibSVM_Datasets(multilabel=False,path='/home/arya/PubMed/GEO/Datasets/'):
    CVTrain=pd.read_pickle(path+'CVTrain.{}.df'.format(('multiclass','multilabel')[multilabel]))
    sys.stdout=open(path.replace('Datasets','Log')+'createds.{}.log'.format(('multiclass','multilabel')[multilabel]),'w')
    sys.stderr=open(path.replace('Datasets','Log')+'createds.{}.err'.format(('multiclass','multilabel')[multilabel]),'w')
    PM=pd.read_pickle(path+'PM.df') 
    PP=pd.read_pickle(path+'PP.df')
    M=pd.read_pickle(path+'M.df')
    PM=pd.merge(PM,M ,left_on=['muid'],right_on=['uid'])[['pmid','mid']]
    PM.index=PM.pmid
    PM.drop('pmid',axis=1,inplace=True)
    PP.index=PP.cites_pmid
    PPM=pd.merge(PP,PM,right_index=True,left_index=True)
    PPM.index=PPM[CVTrain.index.name]
    for fold in range(CVTrain.shape[1]):
        IDX=CVTrain[fold][CVTrain[fold]].index
        ppm=PPM.loc[IDX].dropna()
        print 'creating train dataset...', ppm.index.unique().shape[0], 'out of', ppm.shape[0], sys.stdout.flush()
        labels,feats=create_dataset(ppm)
        print 'writing train dataset...', sys.stdout.flush()
        write_libsvm_dataset_multilabel(labels, feats,'{}libsvm/train.{}.{}.libsvm'.format(path,fold,('multiclass','multilabel')[multilabel]))
        IDX=CVTrain[fold][~CVTrain[fold]].index
        ppm=PPM.loc[IDX].dropna()
        print 'creating test dataset...', ppm.index.unique().shape[0], 'out of', ppm.shape[0], sys.stdout.flush()
        labels,feats=create_dataset(ppm)
        print 'writing test dataset...', sys.stdout.flush()
        write_libsvm_dataset_multilabel(labels, feats,'{}libsvm/test.{}.{}.libsvm'.format(path,fold,('multiclass','multilabel')[multilabel]))
         
        
    
def clean(path='/home/arya/PubMed/GEO/Datasets/',n_fold=5, original_paper_num_citation_th=1):
    sys.stdout=open('/home/arya/PubMed/GEO/Log/clean.log','w')
    print '**************************************************** OriginalPaperCitaionTh= ',original_paper_num_citation_th
    DP=pd.read_pickle(path+'DP.df')
    print 'DP:\n{} Dataset conneced to {} Original Papers (indexed with pmids, not DOI and title). (i.e., N->1  Relationship with max degree ({},{}))\n'.format(DP.accession.unique().shape[0], DP.pmid.unique().shape[0], max(DP.accession.value_counts()), max(DP.pmid.value_counts()) )
    PP=pd.read_pickle(path+'PP.df')
    PP=PP[PP.cited_pmid.isin(DP.pmid.unique())]
    print 'PP:\nAfter Removing Duplicates and Extra Columns and those cited_pmids (original papers) that are not in DP,\nI ended up with {} rows,  {} Unique Original Papers(num_classes) and {} Unique Citations (num_samples in  multilabel classification)).\n'.format(PP.cited_pmid.shape[0], PP.cited_pmid.unique().shape[0], PP.cites_pmid.unique().shape[0])
    keep=PP.cited_pmid.value_counts()>=original_paper_num_citation_th
    PP=PP[PP.cited_pmid.isin(keep[keep].index)]
    print 'PP:\nAfter Removing Original Papers with less than {} citations,\nI ended up with {} rows,  {} Unique Original Papers(num_classes) and {} Unique Citations (num_samples in  multilabel classification)).\n'.format(original_paper_num_citation_th,PP.cited_pmid.shape[0], PP.cited_pmid.unique().shape[0], PP.cites_pmid.unique().shape[0])
    print 'PP is N->N relationship which max degree is ({},{})'.format(max(PP.cited_pmid.value_counts()), max(PP.cites_pmid.value_counts()) )
    PP['sid']=PP.index
    
    DPP = pd.merge(DP,PP, left_on=['pmid'] ,right_on=[ 'cited_pmid'])
    print '\nDPP:\nAfter Merging DP with PP,\nDPP ended up with {} rows, {} unique datasets, {} unique original papers and {} unique cited papers'.format(DPP.shape[0], DPP.accession.unique().shape[0], DPP.cited_pmid.unique().shape[0], DPP.cites_pmid.unique().shape[0])
    
    DPP.to_pickle(path+'DPP.df')
    PP.to_pickle(path+'PP.df')
    DP.to_pickle(path+'DP.df')
#     PMID=set.union(set(PP.cited_pmid.values),set(PP.cites_pmid.values))
#     with open('/home/arya/PubMed/GEO/PMID/pmid.txt','w') as f:
#         for p in PMID:
#             print >>f,p
#     sys.stdout=old_stdout
    
def split(multilabel, path='/home/arya/PubMed/GEO/Datasets/', n_fold=5):
    from sklearn.cross_validation import KFold
    PP= pd.read_pickle(path+'PP.df')
    if multilabel:
        CVTrain=pd.DataFrame(index=PP.cites_pmid.unique(), columns=range(n_fold))
        CVTrain.index.name='cites_pmid'
    else:
        CVTrain=pd.DataFrame(index=PP.sid, columns=range(n_fold))
    kf = KFold(CVTrain.shape[0], n_folds=n_fold)
    for fold,(train_idx, test_idx) in zip(range(n_fold),kf):
        CVTrain[fold].iloc[train_idx]= True
        CVTrain[fold].iloc[test_idx]= False    
    CVTrain=CVTrain.astype(bool) # critical because we are going to not this     
    print CVTrain
    print 'Number of non-NAs in each fold (column)'
    print CVTrain.count() 
    print 'Number of training cases in each fold (column)'
    print CVTrain.sum()
    print 'Making it boolean'
    CVTrain.to_pickle('{}CVTrain.{}.df'.format(path, ('multiclass','multilabel')[multilabel]))
    

        
if __name__ == '__main__':
#     gse_dataset_stats()
#     gse_paper_stats()
#     create_MeSH_features_only_original_papers()

#     clean(original_paper_num_citation_th=50)
#     split(multilabel=False)
#     split(multilabel=True)
# 
#     create_MeSH_LibSVM_Datasets(multilabel=False)
    create_MeSH_LibSVM_Datasets(multilabel=True)
    print 'Done!'    
        
    
    
