'''
Created on Jun 29, 2015

@author: arya
'''
from Bio import Entrez
import pandas as pd
import numpy as np
import sys
Entrez.email="a@a.com"


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
    pd.DataFrame(results,columns=['accession','pmid','result']).to_pickle(path+'Query.GEO.Results.df')
    

if __name__ == '__main__':
    runQueriesGEO()
    print  'Done'

    

