from Bio import Entrez
import os
import numpy as np
import datetime
from Bio.DocSQL import Query
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
        return '{}/{}/{}'.format(date.year,date.month,date.day)
    
    @staticmethod
    def getDate(path , today=False):
        if today:
            now = datetime.date.today()- datetime.timedelta(20000) # from begining to yesterday
            return (now) 
        else:
            files = [ f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
            dates = [datetime.date(1800,01,01)]
            for f in files:
                if  f[:5]=='pmid_' and f[-4:]=='.txt':
                    dates.append(MEDLINEServer.getDateFromStr(f[5:-4].split('_to_')[1].replace('_','/')))
            return (max(dates)+datetime.timedelta(1)) # from the day after last update
            
    
    
    @staticmethod
    def writePMID(f,query):
        handle = Entrez.esearch(db='pubmed',term=query, retmax=100000)
        records = Entrez.read(handle)
        handle.close()
        records = map(int,records['IdList'])
        for rec in records:
            print >> f, rec
    
    @staticmethod
    def getQueries(start,end):
        global TOTAL
        query="(\"{}\"[Date - Entrez] : \"{}\"[Date - Entrez])".format(MEDLINEServer.getStrFromDate(start),MEDLINEServer.getStrFromDate(end))
        handle = Entrez.esearch(db='pubmed',term=query,retmax=1)
        total = int(Entrez.read(handle)['Count'])
        if total<=100000:
            TOTAL+=total
            return query
        else:
            mid=(end-start).days/2
            print '({},{}) -> ({},{}) + ({},{})'.format(start,end, start, start + datetime.timedelta(mid), start+ datetime.timedelta(mid), end),mid,total
            return [MEDLINEServer.getQueries(start, start + datetime.timedelta(mid-1)), MEDLINEServer.getQueries(start+ datetime.timedelta(mid), end)]
    
    @staticmethod
    def updatePMIDs(path='/home/arya/PubMed/PMID/'):
        if not os.path.exists(path):            os.makedirs(path)
        start =  MEDLINEServer.getDate(path, False)
        end   =  MEDLINEServer.getDate(path, not False)
        query="(\"{}\"[Date - Entrez] : \"{}\"[Date - Entrez])".format(MEDLINEServer.getStrFromDate(start),MEDLINEServer.getStrFromDate(end))
        fname=path+'pmid_'+query.replace('/', '_').replace('"','').replace(' : ','_to_').replace('[Date - Entrez]','').replace('(','').replace(')','')+'.txt'
        handle = Entrez.esearch(db='pubmed',term=query,retmax=1)
        total = int(Entrez.read(handle)['Count'])
        print query ,total
        queries = flatten(MEDLINEServer.getQueries(start, end))
        with open(fname,'w') as f:
            for query in queries:
                MEDLINEServer.writePMID(f, query)
        print '\nTotal of {} records fetched from query and total of {} is written to file.'.format(total,len(open(fname).readlines()))
        print TOTAL 
    
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
            print  'Batch File Name Exist!',outPath
            return
        handle = Entrez.efetch(db='pubmed',id=pmidList, retmode="xml")
        with open(outPath,'w') as f:
            for line in handle.readlines():
                print >>f, line,
        
    @staticmethod
    def saveMEDLINE(path='/home/arya/PubMed/', pmidFile='pmid_1800_01_01_to_2015_06_09.txt',num_threads=20):
        outPath=path+'MEDLINE/'
        if not os.path.exists(outPath):
            os.makedirs(outPath)
        outPath+='raw/'
        if not os.path.exists(outPath):
            os.makedirs(outPath)
        savedBatches = [ f for f in os.listdir(outPath) if os.path.isfile(os.path.join(outPath,f)) ]
        pmidpath= path+pmidFile
        PMID=np.array(open(pmidpath).readlines())
        N = len(PMID)
        batch_size=10000
        num_batches= N/batch_size  +1
        print 'Num PMIDs: {}    Num Batches: {}    Num Threads: {}'.format(N,num_batches, num_threads)
        exit()
        from multiprocessing import Pool
        params=[{'pmidList':PMID[range(j*batch_size, min((j+1)*batch_size,N))] , 'outPath' : outPath + 'batch_{}.xml'.format(j)} for j in range(num_batches)]
        pool = Pool(num_threads)
        pool.map(saveBatchHelper,params)
            
    
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
    @staticmethod
    def parseBatch(path):
#         dbpath=outdir+'medline.db'
        param=MEDLINEServer.batchParamForDatabase()
        with open(path) as f:
#             f = Entrez.efetch(db='pubmed',id='26053938', retmode="xml")
#             f = Entrez.efetch(db='pubmed',id='23817699', retmode="xml")
#             f = Entrez.efetch(db='pubmed',id='10540283', retmode="xml")
            records = Entrez.parse(f)
            i=0
            for record in records:
                i+=1
            print i
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
    
if __name__ == '__main__':
    MEDLINEServer.updatePMIDs()
#     MEDLINEServer.saveMEDLINE()
#     MEDLINEServer.parseBatch('/home/arya/PubMed/MEDLINE/raw/batch_916.xml')
    print 'Done!'