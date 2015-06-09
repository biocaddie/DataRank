from Bio import Entrez

def retMEDLINE(pmidList,medlineDir):
    """retrieve MEDLINE with provided PMID"""
    if not os.path.exists(medlineDir):
        Entrez.email=raw_input("Enter your email address to set the Entrez email parameter.\nPlease see http://biopython.org/DIST/docs/api/Bio.Entrez-module.html for more inofrmation.\nYour email: ")
        _retMEDLINE(pmidList,medlineDir)
    
def _retMEDLINE(pmidList,medlineDir):
    handle=Entrez.efetch(db='pubmed',id=pmidList,rettype="medline",retmode="text")
    data=handle.read()
    handle.close()
#     ## save xml files to disk
    outhandle = file(medlineDir,"w")
    outhandle.write(data)
def get_pmids():
    Entrez.email="a@a.com"
    query ="(\"1800/01/01\"[Date - Entrez] : \"2015/06/09\"[Date - Entrez])"
    handle = Entrez.esearch(db="pubmed", term=query,retmax=1)
    fname='pmid_'+query.replace('/', '_').replace('"','').replace(' : ','_to_').replace('[Date - Entrez]','').replace('(','').replace(')','')+'.txt'
    print  fname
    records = Entrez.read(handle)
    total = int(records['Count'])
    count=0
    start=1
    batch_size=100000
    print 'Total',total
    with open(fname,'w') as f:
        while count<total:
            handle = Entrez.esearch(db="pubmed", term="{}[uid]:{}[uid]".format(start, start+batch_size-1), retmax=100000)
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
    
if __name__ == '__main__':
    get_pmid()
    
#         handle = Entrez.esearch(db="pubmed", term="1[uid]:100000[uid]".format(), retmax=200000)
        
#     handle = Entrez.esearch(db="pubmed", term="1[uid]:100000[uid]", retmax=200000)
#     records = Entrez.read(handle)
#     records['IdList'] = map(int,records['IdList'])
#     print len(records['IdList'])
#     print type(records['IdList'])
#     print max(records['IdList'])
#     print min(records['IdList'])
#     print type(int(records['IdList'][0]))
#     for id in records['IdList']:
#         print id
    
    
#     Parsing
#     a=map(str,range(9990,10000))
#     handle = Entrez.efetch("pubmed", id="19304878,14630660", retmode="xml")
#     handle = Entrez.efetch("pubmed", id=a, retmode="xml")
# #     records = Entrez.parse(handle)
#     with open('test.txt','w') as f:
#         for line in handle.readlines():
#             print >>f, line,
# #     for record, i in zip(handle,a):
#     with open('test.txt') as f:
#         records = Entrez.parse(f)
#         for record in records:
#             print record
#             print 'title'   ,record['MedlineCitation']['Article']['ArticleTitle']
#             print 'pmid'    ,record['MedlineCitation']['PMID']
#             print 'abstract' ,record['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
#             print 'date' ,record['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']
#             print 'lang' ,record['MedlineCitation']['Article']['Language']
#             print 'issn' ,record['MedlineCitation']['Article']['Journal']['ISSN']
#             print 'issn' ,record['MedlineCitation']['MeshHeadingList']
#             print 'author' ,record['MedlineCitation']['Article']['AuthorList'][0]
#             print 'fname' ,record['MedlineCitation']['MedlineJournalInfo']['MedlineTA']
#             print 'country' ,record['MedlineCitation']['MedlineJournalInfo']['Country']
#             print 'jid' ,record['MedlineCitation']['MedlineJournalInfo']['NlmUniqueID']
#             print 'issn' ,record['MedlineCitation']['MedlineJournalInfo']['ISSNLinking']
# #             print record.keys()
# #             for k in record.keys():
# #                 print record[k].keys() 
# #                 print ' -----'
# #                 for kk in record[k].keys():
# #                     print k,'.',kk
# #                     print record[k][kk]
# #                 print '****'
#             
#             break