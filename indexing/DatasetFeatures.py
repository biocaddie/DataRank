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
    for k,v in clean_dic(PP).items():
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
    

def create_dataset(df,PM,MeSH):
    labels, feats=[],[]
    j=0
    for _,row in df.iterrows():
        feat={}
        try:
            feat.update(MeSH.loc[PM[row.cited_pmid]].value_counts().to_dict())
        except:
            pass
        try:
            feat.update(MeSH.loc[PM[row.cites_pmid]].value_counts().to_dict())
        except:
            pass
        if len(feat):
            feats.append(feat)
            labels.append( row.did)
        else:
            j+=1
    print '{} were unsucessful, out of {}'.format(j,df.shape[0])
    return labels,feats
    

def write_libsvm_dataset(labels, feats,path):
    with open(path,'w') as f:
        for label,feat in zip(labels, feats):
            line=str(label)
            for k,v in sorted(feat.items(),key=lambda x: x[0]):
                line+=' {}:{}'.format(k,v)
            print >>f,line

def create_MeSH_features(path='/home/arya/PubMed/GEO/Datasets/'):
    IDX=pickle.load(open(path+'DPP.CV.pkl','rb'))
    PM=clean_dic(pd.read_pickle(path+'PMeSH.pkl'))
    DPP=pd.read_pickle(path+'DPP.df')
    MeSH=pd.read_pickle(path+'MeSH.df').mid
    for fold in range(len(IDX['trains'])):
        train=DPP[DPP.sid.isin(IDX['trains'][fold])][['did','cited_pmid','cites_pmid']]
        print 'creating train dataset...', train.shape
        labels,feats=create_dataset(train, PM,MeSH)
#         pickle.dump({'labels':labels,'feats':feats}, open('{}train.{}.pkl'.format(path,fold),'wb'))
        print 'writing train dataset...'
        write_libsvm_dataset(labels, feats,'{}libsvm/train.{}.libsvm'.format(path,fold))
        test =DPP[DPP.sid.isin(IDX['tests'][fold])][['did','cited_pmid','cites_pmid']]
        print 'creating test dataset...', test.shape
        labels,feats=create_dataset(test, PM, MeSH)
#         pickle.dump({'labels':labels,'feats':feats}, open('{}test.{}.pkl'.format(path,fold),'wb'))
        print 'writing test dataset...'
        write_libsvm_dataset(labels, feats,'{}libsvm/test.{}.libsvm'.format(path,fold))
        

        
    
def convert_to_df(path='/home/arya/PubMed/GEO/Datasets/',n_fold=10):
    M=pickle.load(open('/home/arya/PubMed/MeSH/mesh.pkl'))
    M=pd.DataFrame(M)
    M['mid']=M.index
    M.index=M.uid
    print 'MeSH Dictionary has {} terms ({} are distinct)'.format(M.uid.shape[0], M.uid.unique().shape[0])
    M.drop('uid',axis=1,inplace=True)
    
    
    
    DP = pd.DataFrame([value.values() for (_, value) in pickle.load(open(path+'DP.pkl','rb')).items()], columns=('pmid','title','dname','summary'))
    DP.drop_duplicates(inplace=True)
    DP['did']=DP.index
    DP=DP[['did','dname', 'pmid']].dropna()
    print 'DP:\n{} Dataset conneced to {} Original Papers (with pmids not DOI and title). (i.e., N->1  Relationship with max degree ({},{}))\n'.format(DP.dname.unique().shape[0], DP.pmid.unique().shape[0], max(DP.dname.value_counts()), max(DP.pmid.value_counts()) )
    D=DP[['did','dname']].dropna()
    D.index=D.dname
    D.drop('dname',axis=1, inplace=True)
    
    
    PP=create_df(pickle.load(open(path+'citations.pkl','rb')), columns=('cited_pmid','cites_doi','cites_pmid','cites_title', 'cites_num_citaion'))
    PP.drop_duplicates(inplace=True)
    PP.drop(['cites_doi','cites_title'], axis=1, inplace=True)
    PP=PP[PP.cited_pmid.isin(DP.pmid.unique())]
    print 'PP:\nAfter Removing Duplicates and Extra Columns and those cited_pmids (original papers) that are not in DP,\nI ended up with {} rows,  {} Unique Original Papers(num_classes) and {} Unique Citations (num_samples in  multilabel classification)).\n'.format(PP.cited_pmid.shape[0], PP.cited_pmid.unique().shape[0], PP.cites_pmid.unique().shape[0])
    
    PP=PP[['cites_pmid','cited_pmid', 'cites_num_citaion']].dropna() # remove all rows with None (zero citation papers)
    th=10
    keep=PP.cited_pmid.value_counts()>th
    PP=PP[PP.cited_pmid.isin(keep[keep].index)]
    print 'PP:\nAfter Removing Original Papers whith less than {} citations,\nI ended up with {} rows,  {} Unique Original Papers(num_classes) and {} Unique Citations (num_samples in  multilabel classification)).\n'.format(th,PP.cited_pmid.shape[0], PP.cited_pmid.unique().shape[0], PP.cites_pmid.unique().shape[0])
    print 'PP is N->N relationship which max degree is ({},{})'.format(max(PP.cited_pmid.value_counts()), max(PP.cites_pmid.value_counts()) )
    PP['sid']=PP.index
    
    DPP = pd.merge(DP,PP, left_on=['pmid'] ,right_on=[ 'cited_pmid'])
    print '\nDPP:\nAfter Merging DP with PP,\nDPP ended up with {} rows, {} unique datasets, {} unique original papers and {} unique cited papers'.format(DPP.shape[0], DPP.did.unique().shape[0], DPP.cited_pmid.unique().shape[0], DPP.cites_pmid.unique().shape[0])
    
    DPP.to_pickle(path+'DPP.df')
    PP.to_pickle(path+'PP.df')
    D.to_pickle(path+'D.df')
    M.to_pickle(path+'MeSH.df')
    DP.to_pickle(path+'DP.df')
    PMID=set.union(set(PP.cited_pmid.values),set(PP.cites_pmid.values))
    with open('/home/arya/PubMed/GEO/PMID/pmid.txt','w') as f:
        for p in PMID:
            print >>f,p

    
def create_df(dic, columns=None):
    for k,V in dic.items():
        if V:
            for v in V:
                if isinstance(v,tuple):
                    is_tuple=True
                else:
                    is_tuple=False
            break
    tuples=[]
    if is_tuple:
        for k,V in dic.items():
            if V:
                for v in V:
                    tuples.append((k,)+v)
            else:
                tuples.append((k,V))
    else:
        for k,V in dic.items():
            if V:
                for v in V:
                    tuples.append((k,v))
            else:
                tuples.append((k,V))
    if columns:
        return pd.DataFrame(tuples,columns=columns )
    else:
        return pd.DataFrame(tuples)



def split(path='/home/arya/PubMed/GEO/Datasets/', n_fold=5):
    from sklearn.cross_validation import KFold
    PP= pd.read_pickle(path+'PP.df')
    trains,tests= [[] for _ in range(n_fold)], [[] for _ in range(n_fold)]
    OP=PP.cited_pmid.unique()
    CVTrain=pd.DataFrame(index=PP.sid, columns=range(n_fold))
    for op in OP:
        opP=PP.loc[PP.cited_pmid==op]
        kf = KFold(opP.shape[0], n_folds=n_fold)
        for fold,(train_idx, test_idx) in zip(range(n_fold),kf):
            CVTrain[fold].loc[opP.iloc[train_idx].sid]= True
            CVTrain[fold].loc[opP.iloc[test_idx ].sid]=False
        
    print CVTrain
    print 'Number of non-NAs in each fold (column)'
    print CVTrain.count() 
    print 'Number of training cases in each fold (column)'
    print CVTrain.sum()
    print 'Making it boolean'
    CVTrain=CVTrain.astype(bool)
    print CVTrain
    print 'Number of non-NAs in each fold (column)'
    print CVTrain.count() 
    print 'Number of training cases in each fold (column)'
    print CVTrain.sum()
    
    CVTrain.to_pickle(path+'CVTrain.pkl')

    
def create_GEO_Queries(path='/home/arya/PubMed/GEO/Datasets/'):
    DPP= pd.read_pickle(path+'DPP.df')   
    PM= pd.read_pickle(path+'PMeSH.pkl')
    IDX=pd.read_pickle(path+'DPP.CV.pkl')
    M=pd.read_pickle(path+'MeSH.df').name
    labels=[]
    queries=[]
    for i in range(len(IDX['tests'])):
    	pmid=DPP.loc[IDX['tests'][i]].cites_pmid.values
    	for p in pmid:
#     	    DPP[DPP.cites_pmid=='24347632'] 
    	    muid=PM[p]
    	    names=M.loc[muid]
        break



if __name__ == '__main__':
    
#     gse_dataset_stats()
#     gse_paper_stats()
#     create_MeSH_features_only_original_papers()

#     convert_to_df()
    split()
#     create_MeSH_features()
#     create_GEO_Queries()
    print 'Done!'    
        
    
    
