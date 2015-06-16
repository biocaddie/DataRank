from Bio import Entrez
import os
import numpy as np
import datetime
from multiprocessing import Pool
import sys
Entrez.email="a@a.com"
TOTAL=0
def flatten(iterable):
    """Recursively iterate lists and tuples.
    """
    for elm in iterable:
        if isinstance(elm, (list, tuple)):
            for relm in flatten(elm):
                yield relm
        else:
            yield elm
            
def saveBatchHelper( params):
    return MEDLINEServer.saveBatch(**params)

class MEDLINEServer:
    @staticmethod
    def getDateFromStr(str):
        p=map(lambda x: int(x),str.split('/'))
        return datetime.date(p[0],p[1],p[2])
    
    @staticmethod
    def getStrFromDate(date):
        return '{:04}/{:02}/{:02}'.format(date.year,date.month,date.day)
    
    @staticmethod
    def getDate(path , today=False):
        if today:
            now = datetime.date.today()- datetime.timedelta(1) # update until yestedray
            return (now) 
        else:
            files = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
            dates = [datetime.date(1800,01,01)]
            for f in files:
                if  f[:5]=='pmid_' and f[-4:]=='.txt':
                    dates.append(MEDLINEServer.getDateFromStr(f[5:-4].split('_to_')[1].replace('_','/')))
            return (max(dates)+datetime.timedelta(1)) # from the day after last update
            
    @staticmethod
    def updatePMIDs(path='/home/arya/PubMed/PMID/'):
        if not os.path.exists(path):            os.makedirs(path)
        start =  MEDLINEServer.getDate(path, False)
        end   =  MEDLINEServer.getDate(path, not False)
        query="(\"{}\"[Date - Entrez] : \"{}\"[Date - Entrez])".format(MEDLINEServer.getStrFromDate(start),MEDLINEServer.getStrFromDate(end))
        fname=path+'pmid_'+query.replace('/', '_').replace('"','').replace(' : ','_to_').replace('[Date - Entrez]','').replace('(','').replace(')','')+'.txt'
        handle = Entrez.esearch(db='pubmed',term=query,retmax=1)
        total = int(Entrez.read(handle)['Count'])
        print 'Total of',total, 'is found from the query',query
        batch_size=100000
        num_batches= total/batch_size
        if not total:
            return
        with open(fname,'w') as f:
            for j in range(num_batches+1):
                handle = Entrez.esearch(db='pubmed',term=query, retmax=batch_size,retstart=j*batch_size)
                records = Entrez.read(handle)
                handle.close()
                records = map(int,records['IdList'])
                for rec in records:
                    print >> f, rec
    
    @staticmethod 
    def loadPMIDs(path):
        files = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
        dates = np.array([])
        fnames= np.array([])
        for f in files:
            if  f[:5]=='pmid_' and f[-4:]=='.txt':
                dates=np.append(dates, f[5:-4].split('_to_')[1].replace('_','/'))
                fnames=np.append(fnames,f)
        indices = range(len(fnames))
        indices.sort(lambda x,y: cmp(dates[x], dates[y]))
        PMID=[]
        for f in fnames[indices]:
            PMID+= open(path+ f).readlines()
#             PMID+= map(lambda x: int(x.strip()), open(path+ f).readlines())
#         PMID=MEDLINEServer.removeDuplicates(PMID)
        print '{} PMID is returned until {}'.format(len(PMID), dates[indices][-1])
        return np.array(PMID)
    
    @staticmethod
    def getNumRecsordsInBatch(fname):
        records = Entrez.parse(open(fname))
        i=0
        for record in records:
            i+=1
        return i
    
    @staticmethod
    def removeDuplicates(seq):
        seen = set()
        seen_add = seen.add
        return [ x for x in seq if not (x in seen or seen_add(x))]

    @staticmethod    
    def savePMIDs(path='/home/arya/PubMed/'):
        query ="(\"1800/01/01\"[Date - Entrez] : \"2015/06/09\"[Date - Entrez])"
        handle = Entrez.esearch(db='pubmed',term=query,retmax=1)
        if not os.path.exists(path):
            os.makedirs(path)
        fname=path+'pmid_'+query.replace('/', '_').replace('"','').replace(' : ','_to_').replace('[Date - Entrez]','').replace('(','').replace(')','')+'.txt'
        records = Entrez.read(handle)
        total = int(records['Count'])
        count=0
        start=1
        batch_size=100000
        print 'Total',total
        with open(fname,'w') as f:
            while count<total:
                handle = Entrez.esearch(db='pubmed',term="{}[uid]:{}[uid]".format(start, start+batch_size-1), retmax=100000)
                records = Entrez.read(handle)
                handle.close()
                records = map(int,records['IdList'])
                for rec in records:
                    print >> f, rec
                start+=batch_size
                count+=len(records)
                print count,
                if not (count/batch_size)%10 and (count/batch_size):
                    print
        print '\nTotal:',total , 'Count', count
    

    @staticmethod
    def saveBatch(pmidList,outPath):
        pmidList=','.join(pmidList)
        if os.path.exists(outPath):
            try:
                n =MEDLINEServer.getNumRecsordsInBatch(outPath)
                print  'Skipping Batch {} , which has {} records.'.format(outPath, n)
                if n ==10000:
                    return
            except:
                pass
        handle = Entrez.efetch(db='pubmed',id=pmidList, retmode="xml")
        with open(outPath,'w') as f:
            for line in handle.readlines():
                print >>f, line,
    
    @staticmethod
    def saveMEDLINE(path='/home/arya/PubMed/', num_threads=20):
        PMID=MEDLINEServer.loadPMIDs(path+'PMID/')
        outPath=path+'MEDLINE/'
        if not os.path.exists(outPath): os.makedirs(outPath)
        outPath+='raw/'
        if not os.path.exists(outPath): os.makedirs(outPath)
        N = len(PMID)
        batch_size=10000
        num_batches= N/batch_size  +1
        print 'Num PMIDs: {}    Num Batches: {}    Num Threads: {}'.format(N,num_batches, num_threads)
        
        params=[{'pmidList':PMID[range(j*batch_size, min((j+1)*batch_size,N))] , 'outPath' : outPath + 'batch_{}.xml'.format(j)} for j in range(num_batches)]
        pool = Pool(num_threads)
        pool.map(saveBatchHelper,params)
        pool.terminate()
            
    @staticmethod
    def update():
        MEDLINEServer.updatePMIDs()
        MEDLINEServer.saveMEDLINE()
        
    @staticmethod
    def batchParamForDatabase():
        return {'pmid':[],
                'abstract':[],
                'abstractLength':[],
                'title':[],
                'date':[],
                'language':[],
                'issb':[],
                'mesh':[],
                'journal':[],
                'jid':[],
                'author':[],
                'aid':[],
                'country':[],
                'mid':[],
                'DataBankList':[]
                }
# def parseBatch(path):
# #         dbpath=outdir+'medline.db'
# #     param=MEDLINEServer.batchParamForDatabase()
# #     with open(path) as f:
# #             f = Entrez.efetch(db='pubmed',id='26053938', retmode="xml")
# #             f = Entrez.efetch(db='pubmed',id='23817699', retmode="xml")
# #             f = Entrez.efetch(db='pubmed',id='10540283', retmode="xml")
#         records = Entrez.parse(f)
#         i=0
#         for record in records:
#             i+=1
#         print i
#                 param['pmid'].append(record['MedlineCitation']['PMID'])
#                 try:
#                     param['abstract'].append(record['MedlineCitation']['Article']['Abstract']['AbstractText'][0])
#                     param['abstractLength'].append(len(record['MedlineCitation']['Article']['Abstract']['AbstractText'][0]))
#                 except KeyError:
#                     param['abstract'].append('')
#                     param['abstractLength'].append(0)
#                 param['DataBankList'].append(record['MedlineCitation']['Article']['DataBankList'])
#                 param['title'].append(record['MedlineCitation']['Article']['ArticleTitle'])
#                 param['date'].append(record['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'])
#                 param['lang'].append(record['MedlineCitation']['Article']['Language'])
#                 param['mesh'].append(record['MedlineCitation']['MeshHeadingList'])
#                 param['author'].append(record['MedlineCitation']['Article']['AuthorList'][0])
#                 param['journal'].append(record['MedlineCitation']['MedlineJournalInfo']['MedlineTA'])
#                 param['country'].append(record['MedlineCitation']['MedlineJournalInfo']['Country'])
#                 param['jid'].append(record['MedlineCitation']['MedlineJournalInfo']['NlmUniqueID'])
#                 param['issn'].append(record['MedlineCitation']['MedlineJournalInfo']['ISSNLinking'])
#                 break

def add_record(param,record):
    param['pmid'].append(record['MedlineCitation']['PMID'])
    try:
        param['abstract'].append(record['MedlineCitation']['Article']['Abstract']['AbstractText'][0])
        param['abstractLength'].append(len(record['MedlineCitation']['Article']['Abstract']['AbstractText'][0]))
    except KeyError:
        param['abstract'].append('')
        param['abstractLength'].append(0)
    param['DataBankList'].append(record['MedlineCitation']['Article']['DataBankList'])
    param['title'].append(record['MedlineCitation']['Article']['ArticleTitle'])
    param['date'].append(record['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'])
    param['lang'].append(record['MedlineCitation']['Article']['Language'])
    param['mesh'].append(record['MedlineCitation']['MeshHeadingList'])
    param['author'].append(record['MedlineCitation']['Article']['AuthorList'][0])
    param['journal'].append(record['MedlineCitation']['MedlineJournalInfo']['MedlineTA'])
    param['country'].append(record['MedlineCitation']['MedlineJournalInfo']['Country'])
    param['jid'].append(record['MedlineCitation']['MedlineJournalInfo']['NlmUniqueID'])
    param['issn'].append(record['MedlineCitation']['MedlineJournalInfo']['ISSNLinking'])

def parseBatch(path):
    PD,RD={},{}
    f=open(path)
    records = Entrez.parse(f)
    for record in records:
        if 'MedlineCitation' in record.keys():
            rec=record['MedlineCitation']
            if 'Article' in rec.keys():
                if 'DataBankList' in rec['Article'].keys():
                    for d in rec['Article']['DataBankList']:
    #                     if str(rec['PMID']) in PD.keys(): #updating a record (to be tested)
    #                         for ds in PD[str(rec['PMID'])]:
    #                             repository,accession= ds.spli('/')
    #                             del(RD[repository][RD[repository].index(accession)])
    #                             PD[str(rec['PMID'])]=[]
                        for a in d['AccessionNumberList']:
                            accession=str.decode(a,'unicode-escape')
                            repository = str.decode(d['DataBankName'],'unicode-escape')
                            val=repository+'/'+accession
                            try:
                                PD[str(rec['PMID'])].append(val)
                            except:
                                PD[str(rec['PMID'])]=[val]
                            try:
                                RD[repository].append(accession)
                            except:
                                RD[repository]=[accession]
    print path 
    sys.stdout.flush()
    return {'PD':PD,'RD':RD}
#         param =  add_record(param, record['MedlineCitation'] )


def mesh():
    from meshparse import parse_mesh 
#     path='/home/arya/PubMed/MeSH/sample.xml'
    path='/home/arya/PubMed/MeSH/desc2015.xml'
    records=parse_mesh(path)
    Mnames=[]
    Cnames=[]
    Tnames=[]
    MID=[]
    CID=[]
    TID=[]
    for r in records:
        MID.append(r.ui)
        Mnames.append(r.name)
        if r.ui=='D001205':
            print r.ui, r.name
        for c in r.concepts:
            CID.append(c.ui)
            Cnames.append(c.name)
            for t in c.terms:
                Tnames.append(t.name)
                TID.append(t.ui)
            
        
    print len(MID),len(Mnames)
    print len((CID)),len((Cnames))
    print len(set(CID)),len(set(Cnames))
    print len((TID)),len((Tnames))
    print len(set(TID)),len(set(Tnames))


def process_data_stats(path=None, data=None):
    if data is None:    data=pickle.load(open(path))
    else: data['iter']=0
#     with open(path.replace('.pkl','.log'),'a') as f:
    print  '************************************************'
    print  '{:20}{:10}{:10}'.format('Repository','#Datasets', '#Uniques')
    rd = sorted(map(lambda (k,v): (k,len(v),len(set(v))),data['RD'].items()),key=lambda x: x[1],reverse=True)
    for [k,u,v] in rd:    print  '{:20}{:10}{:10}'.format(k,u,v)
    print  '-------------------------------\n{:20}{:10}{:10}\n'.format('Total',sum(map(lambda (k,u,v):u,rd)),sum(map(lambda (k,u,v):v,rd)))
    print  'Until Batch {:5}, {:7} datasets are found {:7} papers'.format(data['iter'], sum(map(len,data['PD'].values())),len(data['PD'].keys()))
    
# def bipartite(path='/home/arya/PubMed/'):    
#     num_batches = max(map(lambda x: int(x.split('_')[1].split('.')[0]),[ f for f in os.listdir(path+'MEDLINE/raw/') if os.path.isfile(os.path.join(path+'MEDLINE/raw/',f)) ]))+1
#     fileout=path+'Datasets/bipartite.pkl'
#     try:
#         data=pickle.load(open(fileout))
#         PD,RD,start=data['PD'],data['RD'],data['iter']+1
#         open(fileout.replace('.pkl','.log'),'w')
#         print 'Resuming from batch', start
#     except:
#         PD,RD,start={},{},0
#     for j in range(start,num_batches):
#         try:
#             f=open(path+'MEDLINE/raw/batch_{}.xml'.format(j))
#             records = Entrez.parse(f)
#             PD,RD=parseBatch(records,PD,RD)
#             pickle.dump({'PD':PD, 'RD':RD, 'iter':j},open(fileout, 'w'))
#             process_data_stats(fileout)
#         except Exception:
#             import traceback
#             print(traceback.format_exc())
#             print 'error reading or parsing batch' ,j
#             with open(fileout.replace('.pkl','.err'),'a') as f:
#                 print >>f,j


def mergeBipartiteBatchResults(results):
    PD,RD={},{}
    for batch in results:
        PD.update(batch['PD'])
        for k,v in batch['RD'].items():
            if k in RD.keys():
                for i in v:
                    RD[k].append(i)
            else:
                RD[k]=v
    return {'PD':PD,'RD':RD}


def bipartite(path='/home/arya/PubMed/',num_threads=20):    
    num_batches = max(map(lambda x: int(x.split('_')[1].split('.')[0]),[ f for f in os.listdir(path+'MEDLINE/raw/') if os.path.isfile(os.path.join(path+'MEDLINE/raw/',f)) ]))+1
    fileout=path+'Datasets/bipartite.pkl'
    sys.stdout = open(fileout.replace('.pkl','.log'),'w')
    sys.stderr = open(fileout.replace('.pkl','.err'),'w')
    start=0
#     num_batches=start+10
    param=[path+'MEDLINE/raw/batch_{}.xml'.format(j) for j in range(start, num_batches)]
    pool = Pool(num_threads)
    results=pool.map(parseBatch,param)
    pool.terminate()
#     pickle.dump(results,open(fileout,'w'))
#     results = pickle.load(open(fileout))
    print '\nMerging...\n'
    results = mergeBipartiteBatchResults(results)
    process_data_stats( data=results)
    
    
    
        
                
            
        
import pickle
if __name__ == '__main__':
    from time import time
    s=time()
#    f = Entrez.efetch(db='pubmed',id='10540283', retmode="xml")
#    records = Entrez.parse(f)
#    for r  in records:
#        print r
    bipartite()
#     process_data_stats()
#     print MEDLINEServer.getNumRecsordsInBatch(fname)
#     MEDLINEServer.updatePMIDs()
#     MEDLINEServer.saveMEDLINE()
    
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)
