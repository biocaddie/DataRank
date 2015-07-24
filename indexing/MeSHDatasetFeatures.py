'''
Created on Jun 24, 2015

@author: arya
'''
import pandas as pd
import numpy as np
import sys,pickle,os
import pylab as plt

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
    
def word_cloud(row):
    row=row[1]
    path='/home/arya/PubMed/GEO/Datasets/wordcloud/'
    if not os.path.exists(path):            os.makedirs(path)
    from wordcloud import WordCloud
    wordcloud = WordCloud(background_color="white",max_words=80,width=1000,height=1000).generate(' '.join( row.mesh))
    plt.ioff()
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig(path+row.accession+'.low.png',format='png', dpi=50)
#     wordcloud = WordCloud(background_color="white",max_words=200,width=1000,height=1000).generate(' '.join( row.mesh))
#     plt.ioff()
#     plt.imshow(wordcloud)
#     plt.axis("off")
#     plt.savefig(path+row.accession+'.high.png',format='png', dpi=400)


def createDatarankWebCorpus(wordcloud=False):
    path='/home/arya/PubMed/GEO/Datasets/'
    dpp=pd.read_pickle(path+'DPP.df')[['accession','pmid','cites_pmid']].drop_duplicates()
    dpp
    d=pd.read_pickle(path+'D.All.df')
    d
    count=pd.read_pickle(path+'DCC.df')[['accession','cpcc']]
    m=pd.read_pickle(path+'M.df')
    pm=pd.read_pickle(path+'PM.df')
    pm.index=pm.pmid
    pm=pm.loc[dpp.cites_pmid.unique()]
    pm=pd.merge(pm,m,left_on='muid',right_on='uid')[['pmid','name']]
    pmg=pm.groupby('pmid')
    CP=pm.pmid.unique()
    
    
    pm=pd.DataFrame( map(lambda p: (p, pmg.get_group(p).name.unique().tolist())  , CP), columns=['pmid','mesh'])
    
    dppm=pd.merge(dpp,pm,left_on='cites_pmid',right_on='pmid')
    G=dppm.groupby('accession')
    A=dppm.accession.unique()
    dm=pd.DataFrame([(a,[m  for v in G.get_group(a).mesh.values for m in v]) for a in A], columns=['accession','mesh'])
    if wordcloud:
        map(word_cloud ,dm.iterrows())
#         from multiprocessing import Pool
#         pool=Pool(10)
#         pool.map(word_cloud ,dm.iterrows())
    d=pd.merge(dm,d,on='accession')
    d=pd.merge(d, count, on='accession')
    d.to_pickle(path+'D.Web.df')

def createBM25Corpus():
    path='/home/arya/PubMed/GEO/Datasets/'
    dpp=pd.read_pickle(path+'DPP.df')[['accession','pmid','cites_pmid']].drop_duplicates()
    dpp
    d=pd.read_pickle(path+'D.All.df')
    d
    count=pd.read_pickle(path+'DCC.df')[['accession','cpcc']]
    m=pd.read_pickle(path+'M.df')
    pm=pd.read_pickle(path+'PM.df')
    pm.index=pm.pmid
    pm=pm.loc[dpp.cites_pmid.unique()]
    pm=pd.merge(pm,m,left_on='muid',right_on='uid')[['pmid','mid']]
    pmg=pm.groupby('pmid')
    CP=pm.pmid.unique()
    
    pm=pd.DataFrame( map(lambda p: (p, pmg.get_group(p).name.unique().tolist())  , CP), columns=['pmid','mesh'])
    
    
    dppm=pd.merge(dpp,pm,left_on='cites_pmid',right_on='pmid')
    G=dppm.groupby('accession')
    A=dppm.accession.unique()
    bm25=pd.DataFrame([(a,[m  for v in G.get_group(a).mid.values for m in v]) for a in A], columns=['accession','mid'])
    d=pd.merge(dm,d,on='accession')
    d=pd.merge(d, count, on='accession')
    d.to_pickle(path+'D.Web.df')
   
def preprocess(path='/home/arya/PubMed/GEO/Datasets/',n_fold=5, OPCCTH=0):
    sys.stdout=open('/home/arya/PubMed/GEO/Log/clean.OPCCTH{}.log'.format(OPCCTH),'w')
    print '**************************************************** OriginalPaperCitaionTh= ',OPCCTH
    if OPCCTH: path+='OPCCTH'+OPCCTH+'/';
    
    DP=pd.read_pickle(path+'DP.All.df')
    print 'DP:\n{} Dataset conneced to {} Original Papers (indexed with pmids, not DOI and title). (i.e., N->1  Relationship with max degree ({},{}))\n'.format(DP.accession.unique().shape[0], DP.pmid.unique().shape[0], max(DP.accession.value_counts()), max(DP.pmid.value_counts()) )
    PP=pd.read_pickle(path+'PP.All.df')
    PP.index=PP.cited_pmid
    PP=PP.loc[DP.pmid.unique()]
    print 'PP:\nAfter Removing Duplicates and Extra Columns and those cited_pmids (original papers) that are not in DP,\nI ended up with {} rows,  {} Unique Original Papers(num_classes) and {} Unique Citations (num_samples in  multilabel classification)).\n'.format(PP.cited_pmid.shape[0], PP.cited_pmid.unique().shape[0], PP.cites_pmid.unique().shape[0])
    keep=PP.cited_pmid.value_counts()>=OPCCTH
    PP=PP[PP.cited_pmid.isin(keep[keep].index)]
    DP.index=DP.pmid
    PP=pd.concat([PP,pd.DataFrame(map(lambda x: (x,x,0), PP.cited_pmid.unique()),columns=PP.columns)])
    PP.index=PP.cites_pmid
    
    PM=pd.read_pickle(path+'PM.df')
    PP=PP.loc[PM.pmid.unique()]
    print 'PP:\nAfter Removing Original Papers with less than {} citations,\nI ended up with {} rows,  {} Unique Original Papers(num_classes) and {} Unique Citations (num_samples in  multilabel classification)).\nWhic connects to {} datasets.'.format(OPCCTH,PP.cited_pmid.shape[0], PP.cited_pmid.unique().shape[0], PP.cites_pmid.unique().shape[0],DP.loc[PP.cited_pmid.unique()].shape[0])
    print 'PP is N->N relationship which max degree is ({},{})'.format(max(PP.cited_pmid.value_counts()), max(PP.cites_pmid.value_counts()) )
    
    DPP = pd.merge(DP,PP, left_on=['pmid'] ,right_on=[ 'cited_pmid'])
    print '\nDPP:\nAfter Merging DP with PP,\nDPP ended up with {} rows, {} unique datasets, {} unique original papers and {} unique cited papers'.format(DPP.shape[0], DPP.accession.unique().shape[0], DPP.cited_pmid.unique().shape[0], DPP.cites_pmid.unique().shape[0])
    
    
    M=pd.read_pickle(path+'M.df')
    PM.index=PM.pmid
    PM=PM.loc[DPP.cites_pmid.unique()].dropna()
    PM.shape
    PM=pd.merge(PM,M ,left_on=['muid'],right_on=['uid'])
    PM.shape
    CP=PP.cites_pmid.unique()
    CP.shape, DPP.cites_pmid.unique().shape , PP.cites_pmid.unique().shape
    PPM=PP.copy(True)
    G=PPM.groupby('cites_pmid')
    corpus=[]
    for p in CP:
        g=G.get_group(p)
        corpus+=[(g.cited_pmid.unique().tolist(), g.cites_pmid.unique()[0])]
    PPM=pd.DataFrame(corpus, columns=['y','pmid'])
    PPM=pd.merge(PPM,PM[['pmid','mid']] ,on=['pmid'])
    G=PPM.groupby('pmid')
    with open(path+'Corpus.libsvm','w') as f: 
        for i in range(len(CP)):
            g=G.get_group(CP[i])
            print >> f, str(map(int,g.y.iloc[0]))[1:-1].replace(' ','')+' '+ ' '.join([ '{}:{}'.format(k,v) for k,v in g.mid.value_counts().sort_index().iteritems()])
    
    n_fold=5
    from sklearn.cross_validation import KFold  
    Folds=pd.DataFrame(index=CP, columns=range(n_fold))
    kf = KFold(Folds.shape[0], n_folds=n_fold)
    for fold,(train_idx, test_idx) in zip(range(n_fold),kf):
        Folds[fold].iloc[train_idx]= True
        Folds[fold].iloc[test_idx]= False    
    Folds=Folds.astype(bool) # critical because we are going to not this
    print Folds
    Folds.to_pickle('{}Folds.df'.format(path))
    
    
    
    
    DPM=pd.merge(DPP,PM ,left_on=['cites_pmid'],right_on=['pmid'])
    DPM
    G=DPM.groupby('cites_pmid')
    corpus=[]
    for p in CP:
        g=G.get_group(p)
        corpus+=[(g.accession.unique().tolist(), g.name.unique().tolist(), g.cited_pmid.unique().tolist(), g.cites_pmid.iloc[0])]
    corpus=pd.DataFrame( corpus, columns=['accession','mesh','cited_pmid','cites_pmid']) 
    corpus.summary="This is set of queries to be used for the experiments."
    corpus.to_pickle(path+'Corpus.GEO.df')
    
    
    G=PPM.groupby('cites_pmid')
    jaccardRanking=pd.DataFrame( map(lambda p: (p, G.get_group(p).mid.unique().tolist())  , CP), columns=['pmid','mid'])
    jaccardRanking=pd.merge(DPP,jaccardRanking,left_on='cites_pmid',right_on='pmid')
    G=jaccardRanking.groupby('accession')
    A=jaccardRanking.accession.unique()
    jaccardRanking=pd.DataFrame([(a,[m  for v in G.get_group(a).mid.values for m in v]) for a in A], columns=['accession','mid'])
    jaccardRanking.to_pickle(path+'Corpus.jaccardRanking.df')
    
    DPP.to_pickle(path+'DPP.df')
    PP.to_pickle(path+'PP.df')
    DP.to_pickle(path+'DP.df')
#     PMID=set.union(set(PP.cited_pmid.values),set(PP.cites_pmid.values))
#     with open('/home/arya/PubMed/GEO/PMID/pmid.txt','w') as f:
#         for p in PMID:
#             print >>f,p
#     sys.stdout=old_stdout
    
    
    
def compute_imporance_ranking():
    path='/home/arya/PubMed/GEO/Datasets/'
    C=pd.read_pickle(path+'Citations.df')
    C.index=C.cited_pmid
    OPCC=pd.DataFrame(C.cited_pmid.value_counts(),columns=['opcc'])
    CPCC=C[['cited_pmid','cc']].dropna().groupby('cited_pmid').agg('sum').sort('cc', ascending=False)
    DPP=pd.read_pickle(path+'DPP.df')[['accession','cited_pmid']].drop_duplicates()
    DPP=pd.merge(DPP, OPCC,left_on='cited_pmid', right_index=True)
    DPP=pd.merge(DPP, CPCC,left_on='cited_pmid', right_index=True)
    DPP.rename(columns={'cc':'cpcc'},inplace=True)
    
    print DPP.sort(['cpcc'],ascending=False).iloc[:5]
    
    print DPP.sort(['opcc'],ascending=False).iloc[:5]
    DPP.index=DPP.cited_pmid
    DPP.loc[OPCC[:6].index].dropna()
    DPP.loc[CPCC[:5].index].dropna()
    DPP.to_pickle(path+'DCC.df')
        
    
    
    
if __name__ == '__main__':
#     gse_dataset_stats()
#     gse_paper_stats()
#     preprocess(OPCCTH=0)
#     compute_imporance_ranking()
    createDatarankWebCorpus(True)
    print 'Done!'    
        
    
    
