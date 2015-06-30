'''
Created on Jun 29, 2015

@author: arya
'''
from Bio import Entrez
Entrez.email="a@a.com"

def query_geo(query):
    query =r"gse " +query
    handle = Entrez.esearch(db='gds',term=query,retmax=1000)
    records = Entrez.read(handle)
    handle.close()
    records = records['IdList']
    handle = Entrez.efetch(db='gds',id=records, retmode="xml")
    return [i.split()[2] for i in handle if i[:6]=='Series']
    
if __name__ == '__main__':
    print query_geo('smoke')
    print len(query_geo('smoke'))
