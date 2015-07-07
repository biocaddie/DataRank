'''
Created on Jun 29, 2015

@author: arya
'''
from Bio import Entrez
import pandas as pd
import numpy as np
from Measure import MRR,AP
Entrez.email="a@a.com"


def create_MeSHQuery(path='/home/arya/PubMed/GEO/Datasets/'):
    PM=pd.read_pickle(path+'PM.df') 
    DP=pd.read_pickle(path+'DP.df') 
    PP=pd.read_pickle(path+'PP.df')
    M=pd.read_pickle(path+'M.df')
    PM=pd.merge(PM,M ,left_on=['muid'],right_on=['uid'])[['pmid','name']]
    PM.index=PM.pmid
    PM.drop('pmid',axis=1,inplace=True)
    PP.index=PP.cites_pmid
    PPM=pd.merge(PP,PM,right_index=True,left_index=True)[['name','cited_pmid']]
    IDX=PPM.index.unique()
    print 'creating {} queries form MeSH terms...'.format(IDX.shape[0])
    MQ=[]
    for i in IDX:
        q= PPM.loc[i]
        if not len(q.cited_pmid.shape):
            cited_pmid=[q.cited_pmid]
        else:
            cited_pmid=q.cited_pmid
        try:
            meshq='\" OR \"'.join(q.name.values)
        except AttributeError:
            meshq=q['name']
            print meshq
        MQ.append((', '.join(DP[DP.pmid.isin(cited_pmid)].accession.unique()), meshq))
    pd.DataFrame(MQ).to_pickle(path+'MeSH.Query.df')        
            

def create_TitleAbstractQuery(path='/home/arya/PubMed/GEO/Datasets/'):
    P=pd.read_pickle(path+'P.df')[['pmid','title','abstract']]
    P.index=P.pmid 
    DP=pd.read_pickle(path+'DP.df') 
    PP=pd.read_pickle(path+'PP.df')
    PP.index=PP.cites_pmid
    PPP=pd.merge(PP,P,right_index=True,left_index=True)
    IDX=PPP.index.unique()
    print 'creating {} queries form MeSH terms...'.format(IDX.shape[0])
#     with open(path+'Title.queries','w') as ft, open(path+'Abstract.queries','w') as fa:
    TQ=[]
    AQ=[]
    for i in IDX:
        q= PPP.loc[i]
        if len(q.shape)==2:
            cited_pmid=q.cited_pmid
            tq=q['title'].iloc[0]
            aq=q['abstract'].iloc[0]
        else:
            cited_pmid=[q.cited_pmid]
            tq=q['title']
            aq=q['abstract']
        
        targets=', '.join(DP[DP.pmid.isin(cited_pmid)].accession.unique())
        TQ.append((targets,tq))
        AQ.append((targets,aq))
    pd.DataFrame(AQ).to_pickle(path+'Abstract.Query.df')
    pd.DataFrame(TQ).to_pickle(path+'Title.Query.df')

def query_geo(query):
    query = u"({})AND \"gse\"[Filter]".format(query)
    handle = Entrez.esearch(db='gds',term=query,retmax=1000)
    records = Entrez.read(handle)
    handle.close()
    records = records['IdList']
    handle = Entrez.efetch(db='gds',id=records, retmode="xml")
    dname= np.array([i.split()[2] for i in handle if i[:6]=='Series'])
    return dname

        
if __name__ == '__main__':
    path='/home/arya/PubMed/GEO/Datasets/'
    
    run='Abstract.Query.df'
#     run='Title.Query.df'
#     run='MeSH.Query.df'
    
    df=pd.read_pickle(path+run)
    y=map(lambda x: x.split(','),df[0])
    q=df[1]
    n=0
    results=[]
    print run, len(q)
    for i in range(len(q)):
#         print i, y[i], q[i]
        try:
            result= query_geo(q[i].replace(' ', ' OR '))
            results.append((','.join(y[i]), ','.join(result)))
        except:
            pass
    df=pd.DataFrame(results,columns=('target','results')).to_pickle(path+run.replace('.Query.df','.results.df'))
#     print  len(result)
#     create_GEO_Queries()
#     create_TitleAbstractQuery()
#     create_MeSHQuery()
    print 'Done'

