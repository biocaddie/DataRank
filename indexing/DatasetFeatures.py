'''
Created on Jun 24, 2015

@author: arya
'''
import pandas as pd
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

# def create_df(path='/home/arya/PubMed/GEO/Datasets/'):
#     PM = clean_dic(pickle.load(open(path+'PM.pkl','rb')))
#     gse_pmid = clean_dic(pickle.load(open(path+'gse_pmid.pkl','rb')))
#     pmid_gse={v:k for k,v in gse_pmid.items()}
#     PP=pickle.load(open(path+'citations.pkl','rb'))
#     DMeSH={}
#     print '{} papers which {} has citaions.'.format(len(PP),len(clean_dic(PP)))
#     PP= clean_dic(PP)
#     
#     pm_tuples=[]
#     for p,ms in PM.items():
#         for m in ms:
#             pm_tuples.append((p,m))
#     pm_df=pd.DataFrame(pm_tuples)
#     pp_tuples = []
#     for cited_pmid,citaions in PP.items():
#         for item in citaions:
#                 pp_tuples.append((cited_pmid,item[0],item[1],item[2]))
#     
#     df = pd.DataFrame(pp_tuples,columns=('cited_pmid','cites_doi','cites_pmid','cites_title'))
#     print df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None]) ]['cited_pmid']
#     print df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None])  &  df['cites_title'].isin([None]) ]['cited_pmid']
#     PDOI = clean_dic(pickle.load(open(path+'PDOI.pkl','rb')))
#     df2=pd.DataFrame(PDOI.items())
#     
#     print df2
    
#     to_be_redownloaded_citations = (df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None])  &  df['cites_title'].isin([None]) ]['cited_pmid'].unique())
#     pickle.dump(to_be_redownloaded_citations,open(path+'to_be_redownloaded_citations.pkl','wb'))



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
    

def create_MeSH_features_only_original_papers(path='/home/arya/PubMed/GEO/Datasets/'):
    gse_pmid = clean_dic(pickle.load(open(path+'gse_pmid.pkl','rb')))
    PM = clean_dic(pickle.load(open(path+'PM.pkl','rb')))
    DMeSH={}
    for (d,p) in gse_pmid.items():
        if p in PM.keys(): DMeSH[d]=PM[p] 
    print 'There are {} datasets with MeSH terms.'.format(len(DMeSH))
    pickle.dump(DMeSH, open(path+'DMeSHOriginal.pkl','wb'))
    num_mesh=map(lambda (k,v):len(set(v)),DMeSH.items())
    plt.hist(num_mesh,20,histtype='stepfilled')
    plt.xlabel('Number of MeSH')
    plt.ylabel('Datasets')
    plt.show()


def create_MeSH_features(path='/home/arya/PubMed/GEO/Datasets/'):
    PM=pickle.load(open(path+'PM.df','rb'))
    PM['mid_num']=pd.Categorical(PM['mid']).labels
    PP=pickle.load(open(path+'PP.df','rb'))[['cited_pmid','cites_pmid']].dropna()
    DP=pickle.load(open(path+'DP.df','rb'))[['pmid','did']].dropna()
    DP['did_num']=pd.Categorical(DP['did']).labels
    DPP = pd.merge(DP,PP, left_on=['pmid'] ,right_on=[ 'cited_pmid'])
    DPP.drop('pmid', axis=1, inplace=True)
    DPPM = pd.merge(DPP,PM, left_on=['cites_pmid'], right_on=['pmid'])
    DPPM.drop('pmid', axis=1, inplace=True)
    print DPPM
    print ''.format()
#     print PP
#     print DP

        
    
def convert_to_df(path='/home/arya/PubMed/GEO/Datasets/'):
    PM = create_df(pickle.load(open(path+'PM.pkl','rb')),columns=('pmid','mid'))
    PP=create_df(pickle.load(open(path+'citations.pkl','rb')), columns=('cited_pmid','cites_doi','cites_pmid','cites_title', 'cites_num_citaion'))
    PM.drop_duplicates(inplace=True)
    pickle.dump(PM,open(path+'PM.df','wb'))
    PP.drop_duplicates(inplace=True)
    PP['sid']=PP.index
    pickle.dump(PP,open(path+'PP.df','wb'))

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
    import numpy as np
    from sklearn.cross_validation import KFold
    
    PP=pickle.load(open(path+'PP.df','rb'))
    N=PP['cited_pmid'].unique().shape[0]
    print N
    PP=PP.dropna()
    hist=collections.Counter(PP['cited_pmid'])
    keep=[k for k,v in hist.items() if v>n_fold]
    remove=[k for k,v in hist.items() if v<=n_fold or k is None]
    print 'of {} {},  {} have more than {} citations, (removing {}) '.format(N,len(remove)+len(keep), len(keep), n_fold, len(remove))
    PP=PP[PP['cited_pmid'].isin(keep)]
    
    
    pmid_unique=PP['cited_pmid'].unique()
    trains,tests= [[] for _ in range(n_fold)], [[] for _ in range(n_fold)]
    j=0
    for pmid in pmid_unique:
        j+=1
        PPpmid=PP.loc[PP['cited_pmid']==pmid]
        kf = KFold(PPpmid.shape[0], n_folds=n_fold)
        for train, test, (train_idx, test_idx) in zip(trains,tests,kf):
            train+= list(PP.iloc[train_idx]['sid'])
            test+= list(PP.iloc[test_idx]['sid'])
#         if j>2: break
    pickle.dump({'trains':trains, 'tests':tests},open('{}PP.cvidx.pkl'.format(path),'wb'))
    for i in range(n_fold):
        
        
        pickle.dump(tests[i],open('{}PP.{}cv.test.fold{}.df'.format(path,n_fold,i),'wb'))
    
if __name__ == '__main__':
    
#     gse_dataset_stats()
#     gse_paper_stats()
#     create_MeSH_features_only_original_papers()

    convert_to_df()
    split()
#     create_MeSH_features()

        
    
    