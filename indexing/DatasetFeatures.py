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
    mesh=pickle.load(open('/home/arya/PubMed/MeSH/mesh.pkl'))
    mesh=pd.DataFrame(mesh)
    mesh['mid']=mesh.index
    mesh.index=mesh.uid
    mesh.drop('uid',axis=1,inplace=True)
    mesh.to_pickle(path+'MeSH.df')
    
    DP = pd.DataFrame([value.values() for (_, value) in pickle.load(open(path+'DP.pkl','rb')).items()], columns=('pmid','title','dname','summary'))
    DP.drop_duplicates(inplace=True)
    DP['did']=DP.index
    DP.to_pickle(path+'DP.df')
    D=DP[['did','dname']].dropna()
    D.index=D.dname
    D.drop('dname',axis=1, inplace=True)
    D.to_pickle(path+'D.df')
    
    PP=create_df(pickle.load(open(path+'citations.pkl','rb')), columns=('cited_pmid','cites_doi','cites_pmid','cites_title', 'cites_num_citaion'))
    PP.drop_duplicates(inplace=True)
    PP.drop(['cites_doi','cites_title'], axis=1, inplace=True)
    PP.to_pickle(path+'PP.df')
    
    PMID=set.union(set(PP.cited_pmid.values),set(PP.cites_pmid.values))
    print  'writing all pmids in PMID folder for download'
    with open('/home/arya/PubMed/GEO/PMID/pmid.txt','w') as f:
        for p in PMID:
            print >>f,p
    
    
    M= PP.shape[0]
    N=PP['cited_pmid'].unique().shape[0]
    print 'Dropping NA...'
    PP=PP[['cites_pmid','cited_pmid', 'cites_num_citaion']].dropna() # remove all rows with None (zero citation papers)
    PP.index=PP.cited_pmid
    th=46
    print 'Dropping cited paper with less than {} citations...'.format(th)
    keep=PP['cited_pmid'].value_counts()>=th
    keep=keep[keep].index
    PP=PP.loc[keep]
    print 'Dropping cited paper with less than 1 citations...'
    PP=PP[~(PP.cites_num_citaion=='0')]
    print 'of {} original papers, {} have more than {} citations, (removing {}) '.format(N, len(keep), th, N -len(keep))
    print 'of {} citations, {} are corresponding to labels with more than {} samples'.format(M,PP.shape[0],th)
    DP=pd.read_pickle(path+'DP.df')[['did','dname', 'pmid']].dropna()
    print 'Remove duplicate classes (original papers with more than one datasets)...'
    DP=DP[~DP.pmid.duplicated()] # 
    DPP = pd.merge(DP,PP, left_on=['pmid'] ,right_on=[ 'cited_pmid'])
    print 'of {} samples and {} classes (datasets) after joining with {} original papers'.format(DPP.shape[0], DPP.did.unique().shape[0], DPP.cited_pmid.unique().shape[0])
    DPP.drop('pmid', axis=1, inplace=True)
    DPP['sid']=DPP.index
    DPP.to_pickle(path+'DPP.df')

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



def split(path='/home/arya/PubMed/GEO/Datasets/', n_fold=10):
    import numpy as np
    from sklearn.cross_validation import KFold
    DPP= pd.read_pickle(path+'DPP.df')
    trains,tests= [[] for _ in range(n_fold)], [[] for _ in range(n_fold)]
    DID=DPP.did.unique()
    for did in DID:
        DPPdid=DPP.loc[DPP.did==did]
        kf = KFold(DPPdid.shape[0], n_folds=n_fold)
        for train, test, (train_idx, test_idx) in zip(trains,tests,kf):
            train+= list(DPPdid.iloc[train_idx].sid)
            test+= list(DPPdid.iloc[test_idx].sid)
#         if j>2: break
    print 'CV trains has {} and CV test has {} samples'.format(len(trains[0]), len(tests[0]))
    pickle.dump({'trains':trains, 'tests':tests},open('{}DPP.CV.pkl'.format(path),'wb'))

    
def create_GEO_Queries(path='/home/arya/PubMed/GEO/Datasets/'):
    DPP= pd.read_pickle(path+'DPP.df')   
    PM= pd.read_pickle(path+'PMeSH.pkl')
if __name__ == '__main__':
    
#     gse_dataset_stats()
#     gse_paper_stats()
#     create_MeSH_features_only_original_papers()

    convert_to_df()
    split()
#     create_MeSH_features()
    
    
        
    
    