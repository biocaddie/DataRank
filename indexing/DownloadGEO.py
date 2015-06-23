'''
Created on Jun 21, 2015

@author: arya
'''
import numpy as np
import pickle,sys,multiprocessing,os, traceback
from Bio import Entrez
Entrez.email="a@a.com"
from ftplib import FTP
outpath='/home/arya/PubMed/GEO/GSE/'
num_threads=20
if not os.path.exists(outpath):            os.makedirs(outpath)
try:
    downloaded=open(outpath+'out.log.txt').readlines()[1:]
except:
    downloaded=[]

def download_one(path):
    try:
        ftp = FTP('ftp.ncbi.nlm.nih.gov') 
        ftp.login()
        ftp.cwd(path)
        files = ftp.nlst()
        for f in files:
            if f in downloaded:
                continue
            fout = open(outpath+f, 'wb')
            ftp.retrbinary('RETR '+f,fout.write)
            print f 
            sys.stdout.flush()
    except:
        print >> sys.stderr, path
    
def download():
    paths=pickle.load(open(outpath+'FTPpaths.pkl','rb'))
    print 'downloading {} files'.format(len(paths))
    sys.stdout = open(outpath+'download.out.txt','a')
    sys.stderr = open(outpath+'download.err.txt','a')
    pool=multiprocessing.Pool(num_threads)
    print 'downloading {} files'.format(len(paths))
    sys.stdout.flush()
    pool.map(download_one, paths)
    print 'Done!'
    
def get_paths():
    ftp = FTP('ftp.ncbi.nlm.nih.gov') 
    ftp.login()
    ftp.cwd('//geo//series')
    parent_dir = ftp.nlst()
    path={p:[] for p in parent_dir}
    all_paths=[]
    ftp.cwd(parent_dir[0])
    for p in parent_dir:
        ftp.cwd('..//'+p)
        path[p] = ftp.nlst()
        all_paths+=['//geo//series//{}//{}//matrix//'.format(p,c) for c in ftp.nlst()]
    pickle.dump(all_paths,open(outpath+'FTPpaths.pkl','wb'))

class GSE:
    def __init__(self):
        self.accession=None
        self.title=None
        self.summary=''
        self.pmid=None

def parse_all():
    sys.stdout = open(outpath+'parse.out.txt','w')
    sys.stderr = open(outpath+'parse.err.txt','w')
    files = [ outpath+f for f in os.listdir(outpath) if os.path.isfile(os.path.join(outpath,f)) ]
    print 'parsing {} files'.format(len(files))
    pool=multiprocessing.Pool(num_threads)
    DS = pool.map(parse_one,files)
    pickle.dump(DS,open(outpath+'GSE.pkl','wb'))
    
def parse_one(path):
    import gzip
    try:
        lines=gzip.open(path,'rb').readlines()
        ds={'accession':None, 'summary':'', 'pmid':None, 'title':None}
        for l in lines:
            fields=l.split('\t')
            fields=map(lambda x: str.strip(x.replace('"',' ').replace('Keywords:','') ),fields)
            if fields[0] == '!Series_geo_accession':
                ds['accession']=fields[1]
            if fields[0] == '!Series_summary'and fields[1] is not None:
                ds['summary']+=fields[1]+' '
            if fields[0] == '!Series_title':
                ds['title']=fields[1]
            if fields[0] == '!Series_pubmed_id':
                ds['pmid']=fields[1]
            if fields[0]=='!series_matrix_table_begin':
                break
        print path 
        sys.stdout.flush()
        return {ds['accession']:ds}
    except:
        print >> sys.stderr, '{}\n{}\n***********'.format(path,traceback.format_exc())
        return None

def merge():
    data_outpath=outpath.replace('GSE','Datasets')
    if not os.path.exists(data_outpath):            os.makedirs(data_outpath)
    all_gse=[x for x in pickle.load(open(outpath+'GSE.pkl','rb')) if x is not None]
    dic={}
    for item in all_gse:
        dic.update(item)
    gse_pmid = {key: value['pmid'] for (key, value) in dic.items()}
    pickle.dump(gse_pmid, open(data_outpath+'gse_pmid.pkl','wb'))
    gse_title = {key: value['title'] for (key, value) in dic.items()}
    pickle.dump(gse_title, open(data_outpath+'gse_title.pkl','wb'))
    gse_summary = {key: value['summary'] for (key, value) in dic.items()}
    pickle.dump(gse_summary, open(data_outpath+'gse_summary.pkl','wb'))
    gse_pmid = {key: value  for (key, value) in gse_pmid.items() if value is not None}
    pickle.dump(gse_pmid, open(data_outpath+'gse_pmid_clean.pkl','wb'))
    with open(outpath.replace('GSE', 'PMID')+'gse_pmid.txt','w') as f:
        for pmid in gse_pmid.values():
            if len(pmid):
                print >>f,pmid 
#     c=np.array(count.values())
#     print sum(c>1)
    
if __name__ == '__main__':
#     get_paths()
#     download()
#     parse_all()
    merge()
    
    