'''
Created on Jun 24, 2015

@author: arya
'''
import pandas as pd
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
    gse_pmid = clean_dic(pickle.load(open(path+'gse_pmid.pkl','rb')))
    pmid_gse={v:k for k,v in gse_pmid.items()}
    PP=pickle.load(open(path+'citations.pkl','rb'))
    DMeSH={}
    for (d,p) in gse_pmid.items():
        if p in PM.keys(): 
            DMeSH[d]=PM[p] 
    for k,v in PP.items():
        print len(v[0])
    for op in pmid_gse.keys():
        for doi,cp,title in PP[op]:
            try:
                DMeSH[pmid_gse[op]].append(PM[cp])
            except:
                print op,cp
                print op in pmid_gse.keys()
                print pmid_gse[op]
    pickle.dump(DMeSH, open(path+'DMeSHAll.pkl','wb'))    
    
    exit()
    print '{} papers which {} has citaions.'.format(len(PP),len(clean_dic(PP)))
    PP= clean_dic(PP)
    
    pm_tuples=[]
    for p,ms in PM.items():
        for m in ms:
            pm_tuples.append((p,m))
    pm_df=pd.DataFrame(pm_tuples)
    pp_tuples = []
    for cited_pmid,citaions in PP.items():
        for item in citaions:
            if len(item)==2:
                pp_tuples.append((cited_pmid,item[0],item[1],None))
            else:
                pp_tuples.append((cited_pmid,item[0],item[1],item[2]))
    
    df = pd.DataFrame(pp_tuples,columns=('cited_pmid','cites_doi','cites_pmid','cites_title'))
    print df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None]) ]['cited_pmid']
    print df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None])  &  df['cites_title'].isin([None]) ]['cited_pmid']
    PDOI = clean_dic(pickle.load(open(path+'PDOI.pkl','rb')))
    df2=pd.DataFrame(PDOI.items())
    
    print df2
    
#     to_be_redownloaded_citations = (df.loc[df['cites_pmid'].isin([None])  &  df['cites_doi'].isin([None])  &  df['cites_title'].isin([None]) ]['cited_pmid'].unique())
#     pickle.dump(to_be_redownloaded_citations,open(path+'to_be_redownloaded_citations.pkl','wb'))


if __name__ == '__main__':
    gse_dataset_stats()
    gse_paper_stats()
    create_MeSH_features_only_original_papers()    
    create_MeSH_features_cited_papers()
#     fix()
    