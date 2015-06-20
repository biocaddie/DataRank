from Bio import Entrez
import os
import numpy as np
import datetime
from multiprocessing import Pool

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
    def saveMEDLINE(path='/home/arya/PubMedGEO/', num_threads=10):
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

        

if __name__ == '__main__':
    from time import time
    s=time()
#     MEDLINEServer.updatePMIDs()
    MEDLINEServer.saveMEDLINE()
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)
