'''
Created on Jun 29, 2015

@author: arya
'''
from Bio import Entrez
import pandas as pd
import numpy as np
import sys
Entrez.email="a@a.com"

def createQueryCorpus(path='/home/arya/PubMed/GEO/Datasets/'):
    M=pd.read_pickle(path+'M.df')
    DPP=pd.read_pickle(path+'DPP.df')
    PM=pd.read_pickle(path+'PM.df')
    PM.index=PM.pmid
    PM=PM.loc[DPP.cites_pmid.unique()].dropna()
    PM
    PM=pd.merge(PM,M ,left_on=['muid'],right_on=['uid'])
    PM
    DPM=pd.merge(DPP,PM ,left_on=['cites_pmid'],right_on=['pmid'])
    DPM
    DPMg=DPM.groupby('cites_pmid')
    uniquep=DPM.cites_pmid.unique()
    Q=[]
    for p in uniquep:
        g=DPMg.get_group(p)
        Q+=[(g.accession.unique().tolist(), g.name.unique().tolist(), g.cited_pmid.unique().tolist(), g.cites_pmid.unique()[0])]
    Q=pd.DataFrame( Q, columns=['accession','mesh','cited_pmid','cites_pmid']) 
#     P=pd.read_pickle(path+'P.df')[['pmid','title','abstract']]
#     Q=pd.merge(Q,P, left_on='cites_pmid',right_on='pmid')
    Q.summary="This is set of queries to be used for the experiments."
    Q.to_pickle(path+'Query.df')        
 #     meshq=           


def queryGEO(row):
    try:
        query= '\"' +  '\" OR \"'.join(row.mesh) +'\"'
        query
        query = u"({}) AND \"gse\"[Filter] AND Fields[All Fields]".format(query)
        query
        handle = Entrez.esearch(db='gds',term=query,retmax=1000)
        records = Entrez.read(handle)
        handle.close()
        records = records['IdList']
        handle = Entrez.efetch(db='gds',id=records, retmode="xml")
        result= np.array([i.split()[2] for i in handle if i[:6]=='Series'])
        print row.cites_pmid,sys.stdout.flush()
        return (row.accession,row.cites_pmid, result)
    except:
        print >> sys.stderr,row.cites_pmid,sys.stderr.flush()
        return (row.accession,row.cites_pmid, None)


def runQueriesGEO(path='/home/arya/PubMed/GEO/Datasets/'):
    sys.stdout=open(path.replace('Datasets', 'Log')+'Query.MeSH.GEO.log','w')
    sys.stderr=open(path.replace('Datasets', 'Log')+'Query.MeSH.GEO.err','w')
    Q=pd.read_pickle(path+'Query.df')
    print 'Searching Queries in GEO:',Q.shape[0]
    results=[]
    for _,row in Q.iterrows():
        results.append( queryGEO(row))
    pd.DataFrame(results,columns=['accession','pmid','result']).to_pickle(path+'Query.MeSH.GEO.Results.df')
    

if __name__ == '__main__':
#     createQueryCorpus()    
    runQueriesGEO()
    print  'Done'

    

