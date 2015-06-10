from Bio import Entrez
import os
class MEDLINEServer:
    @staticmethod    
    def get_pmids(path='/home/arya/PubMed/'):
        Entrez.email="a@a.com"
        query ="(\"1800/01/01\"[Date - Entrez] : \"2015/06/09\"[Date - Entrez])"
        handle = Entrez.esearch(term=query,retmax=1)
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
                handle = Entrez.esearch(term="{}[uid]:{}[uid]".format(start, start+batch_size-1), retmax=100000)
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
        print 'Total:',total , 'Count', count
    
    
    @staticmethod
    def save(pmidList,outPath):
        if not os.path.exists(path):
            os.makedirs(outPath)
        pmidList=','.join(pmidList)
        handle = Entrez.efetch(id=a, retmode="xml")
        with open(outOath,'w') as f:
            for line in handle.readlines():
                print >>f, line,
    
    @staticmethod
    def parse(path):
        with open(path) as f:
            records = Entrez.parse(f)
            for record in records:
                print record
                print 'title'   ,record['MedlineCitation']['Article']['ArticleTitle']
                print 'pmid'    ,record['MedlineCitation']['PMID']
                print 'abstract' ,record['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
                print 'date' ,record['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']
                print 'lang' ,record['MedlineCitation']['Article']['Language']
                print 'issn' ,record['MedlineCitation']['Article']['Journal']['ISSN']
                print 'issn' ,record['MedlineCitation']['MeshHeadingList']
                print 'author' ,record['MedlineCitation']['Article']['AuthorList'][0]
                print 'fname' ,record['MedlineCitation']['MedlineJournalInfo']['MedlineTA']
                print 'country' ,record['MedlineCitation']['MedlineJournalInfo']['Country']
                print 'jid' ,record['MedlineCitation']['MedlineJournalInfo']['NlmUniqueID']
                print 'issn' ,record['MedlineCitation']['MedlineJournalInfo']['ISSNLinking']
                break
    
if __name__ == '__main__':
    print 'Done!'