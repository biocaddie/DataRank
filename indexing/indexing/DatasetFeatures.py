'''
Created on Jun 24, 2015

@author: arya
'''
import sys,pickle,os
import pylab as plt
def clean_dic(dic):
    dic2={key: value  for (key, value) in dic.items() if value is not None and key is not None}
    return {key: value  for (key, value) in dic2.items() if len(value)}

def gse_dataset_stats(path='/home/arya/PubMed/GEO/Datasets/'):
    gse_pmid = pickle.load(open(path+'gse_pmid.pkl','rb'))
    gse_summary = pickle.load(open(path+'gse_summary.pkl','rb'))
    gse_title = pickle.load(open(path+'gse_title.pkl','rb'))
    print 'There are total of {} GEO Datasets which only\n{} has PMID\n{} has summary\n{} has title'.format( len(clean_dic(gse_pmid)), len(clean_dic(gse_pmid)), len(clean_dic(gse_summary)), len(clean_dic(gse_title)))

def gse_paper_stats(path='/home/arya/PubMed/GEO/Datasets/'):
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

def create_MeSH_features_cited_papers(path='/home/arya/PubMed/GEO/Datasets/'):
    PM = clean_dic(pickle.load(open(path+'PM.pkl','rb')))
    PP=pickle.load(open(path+'citations.pkl','rb'))
    print '{} papers which {} has citaions.'.format(len(PP),len(clean_dic(PP)))
    PP= clean_dic(PP)
    pp_tuples = []
    for cited_pmid,citaions in PP.items():
        for item in citaions:
            if len(item)==2:
                pp_tuples.append((cited_pmid,item[0],item[1],None))
            else:
                pp_tuples.append((cited_pmid,item[0],item[1],item[2]))
    import pandas as pd
    df = pd.DataFrame(pp_tuples,columns=('cited_pmid','cites_doi','cites_pmid','cites_title'))
    print df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None]) ]['cited_pmid']
    print df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None])  &  df['cites_title'].isin([None]) ]['cited_pmid']
    PDOI = clean_dic(pickle.load(open(path+'PDOI.pkl','rb')))
    df2=pd.DataFrame(PDOI.items())
    print df2
    
#     to_be_redownloaded_citations = (df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None])  &  df['cites_title'].isin([None]) ]['cited_pmid'].unique())
#     pickle.dump(to_be_redownloaded_citations,open(path+'to_be_redownloaded_citations.pkl','wb'))


def fix():
    path='/home/arya/PubMed/GEO/Datasets/'
    redownload= pickle.load(open(path+'to_be_redownloaded_citations.pkl','rb'))
    print len(map(str.strip,open(path+'citaions.log').readlines()))
    citations=list(set(map(str.strip,open(path+'citaions.log').readlines())))
    print len(redownload)
    
    new_citations= [c for c in citations if c not in redownload]
    print len(new_citations)
    print len(citations)
    with open(path+'citations.log','w') as f:
        for c in new_citations:
            print >> f,c
if __name__ == '__main__':
#     gse_dataset_stats()
#     gse_paper_stats()
#     create_MeSH_features()    

    create_MeSH_features_cited_papers()
    