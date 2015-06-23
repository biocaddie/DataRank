'''
Created on Jun 19, 2015

@author: arya
'''
import pickle,sys,multiprocessing,os
import traceback
from Bio import Entrez
Entrez.email="a@a.com"


def to_unicode(string):
    return str.decode(string,'unicode-escape')
    
def insert_dic(dic,k,v):
    if k not in dic.keys():
        dic[k]=[]
    dic[k].append(v)
    return dic


def getDatasets(pmid,dblist,PD,RD):
    for d in dblist:
        for a in d['AccessionNumberList']:
            accession=str.decode(a,'unicode-escape')
            repository = str.decode(d['DataBankName'],'unicode-escape')
            dataset=repository+'/'+accession
            PD=insert_dic(PD, pmid, dataset)
            RD=insert_dic(RD,repository, accession)
    return PD,RD

def getAbstract(article):
    if 'Abstract' in article.keys():
        return u' '.join( article['Abstract']['AbstractText'])
    return None

def getTitle(article):
    if 'ArticleTitle' in article.keys():
        return unicode(article['ArticleTitle'])
    return None

def getYear(article):
    try:
        return article['Journal']['JournalIssue']['PubDate']['Year']
    except KeyError:
        return None
    
def getMonth(article):
    try:
        return article['Journal']['JournalIssue']['PubDate']['Month']
    except KeyError:
        return None

def getJID(article):
    if 'MedlineJournalInfo' in article.keys():
        if 'NlmUniqueID' in article['MedlineJournalInfo'].keys(): 
            return article['MedlineJournalInfo']['NlmUniqueID']
    return None

def getJname(article):
    if 'MedlineJournalInfo' in article.keys():
        if 'MedlineTA' in article['MedlineJournalInfo'].keys(): 
            return article['MedlineJournalInfo']['MedlineTA']
    return None


def getPaper(rec):    
    try:
        return {'abstract':getAbstract(rec['Article']), 'title':getTitle(rec['Article']), 'year':getYear(rec['Article']),'month':getMonth(rec['Article']), 'jid':getJID(rec), 'jname':getJname(rec)}
#         return {'abstract':getAbstract(rec['Article']), 'title':None, 'year':getYear(rec['Article']),'month':getMonth(rec['Article']), 'jid':getJID(rec), 'jname':getJname(rec)}
    except:
        return None

def getMeSH(rec):
    try:
        mesh=[]
        for item in rec['MeshHeadingList']:
            mesh.append(item['DescriptorName'].attributes['UI'])
        return mesh
    except:
        return None        

def getDOI(article):
    if 'ELocationID' in article.keys():
        for doi in article['ELocationID']:
            if doi.__dict__['attributes'][u'EIdType']==u'doi'and doi.__dict__['attributes'][u'ValidYN']==u'Y':
                return unicode(doi)
    return None

def getAuthor(article):    
    alist=[]
    try:
        for item in article['AuthorList']:
            author={}
            try:
                author['name']=item['ForeName']
            except:
                author['name']=None
            try:
                author['family']=item['LastName']
            except:
                author['family']=None
            try:
                author['initial']=item['Initials']
            except:
                author['initial']=None
            alist.append(author)
        return alist
    except:
        return None
def getLanguage(article):    
    try:
        return article['Language']
    except KeyError:
        return None

def parseBatchAll(path):
    P,PD,RD,PA,PM,PL, PDOI, PT={},{},{},{},{},{},{}, {}
    f=open(path)
#     f = Entrez.efetch(db='pubmed',id='10540283', retmode="xml")
#     f = Entrez.efetch(db='pubmed',id='19897313', retmode="xml")
    records = Entrez.parse(f)
    try:
        for record in records:
            if 'MedlineCitation' in record.keys():
                rec=record['MedlineCitation']
                pmid=str(rec['PMID'])
                if 'Article' in rec.keys():
                    if 'DataBankList' in rec['Article'].keys() :
                        PD,RD=getDatasets(pmid, rec['Article']['DataBankList'], PD, RD)
                    article=rec['Article']
                    P[pmid]= getPaper(rec)
                    PA[pmid]=getAuthor(article)
                    PL[pmid]=getLanguage(article)
                    PM[pmid]=getMeSH(rec)
                    PDOI[pmid]= getDOI(article)
                    PT[pmid]= getTitle(article)
    except:
        print >> sys.stderr, '{}\n{}\n***********'.format(path,traceback.format_exc())
    print path 
    sys.stdout.flush()
    return {'PD':PD,'RD':RD, 'P':P, 'PA':PA,'PM':PM,'PL':PL, 'PDOI':PDOI, 'PT':PT}

def parseBatch(path):
    PD,RD={},{}
    f=open(path)
    records = Entrez.parse(f)
    try:
        for record in records:
            if 'MedlineCitation' in record.keys():
                rec=record['MedlineCitation']
                if 'Article' in rec.keys():
                    if 'DataBankList' in rec['Article'].keys():
                        for d in rec['Article']['DataBankList']:
                            for a in d['AccessionNumberList']:
                                accession=to_unicode(a)
                                repository = to_unicode(d['DataBankName'])
                                val=repository+'/'+accession
                                pmid=str(rec['PMID'])
                                if pmid not in PD.keys():
                                    PD[pmid]=[]
                                PD[pmid].append(val)
                                if repository not in RD.keys():
                                    RD[repository]=[]
                                RD[repository].append(accession)
    except:
        print >> sys.stderr, '{}\n{}\n***********'.format(path,traceback.format_exc())
    
    print path 
    sys.stdout.flush()
    return {'PD':PD,'RD':RD}

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

def mergeBipartiteBatchResultsAll(results):
    P,PD,RD,PA,PM,PL, PDOI, PT={},{},{},{},{},{},{}, {}
    for batch in results:
        P.update(batch['P'])
        PD.update(batch['PD'])
        PA.update(batch['PA'])
        PM.update(batch['PM'])
        PL.update(batch['PL'])
        PT.update(batch['PT'])
        PDOI.update(batch['PDOI'])
        for k,v in batch['RD'].items():
            if k in RD.keys():
                for i in v:
                    RD[k].append(i)
            else:
                RD[k]=v
    return {'PD':PD,'RD':RD, 'P':P, 'PA':PA,'PM':PM,'PL':PL, 'PDOI':PDOI, 'PT':PT}


def bipartite(path='/home/arya/PubMed/',num_threads=20):    
    num_batches = max(map(lambda x: int(x.split('_')[1].split('.')[0]),[ f for f in os.listdir(path+'MEDLINE/raw/') if os.path.isfile(os.path.join(path+'MEDLINE/raw/',f)) ]))+1
    fileout=path+'Datasets/bipartite.pkl'
    sys.stdout = open(fileout.replace('.pkl','.log'),'w')
    sys.stderr = open(fileout.replace('.pkl','.err'),'w')
    start=0
#     num_batches=start+10
    param=[path+'MEDLINE/raw/batch_{}.xml'.format(j) for j in range(start, num_batches)]
    pool = multiprocessing.Pool(num_threads)
    results=pool.map(parseBatch,param)
    pool.terminate()
    print '\nMerging...\n'
    results = mergeBipartiteBatchResults(results)
    pickle.dump(results,open(fileout,'wb'))
    process_data_stats( data=results)

def parseAll(runname,path='/home/arya/PubMed/GEO/',num_threads=20):    
    num_batches = max(map(lambda x: int(x.split('_')[1].split('.')[0]),[ f for f in os.listdir(path+'MEDLINE/raw/') if os.path.isfile(os.path.join(path+'MEDLINE/raw/',f)) ]))+1
    fileout=path+'Datasets/{}.pkl'.format(runname)
    sys.stdout = open(fileout.replace('.pkl','.log'),'w')
    sys.stderr = open(fileout.replace('.pkl','.err'),'w')
    start=0
    param=[path+'MEDLINE/raw/batch_{}.xml'.format(j) for j in range(start, num_batches)]
    
#     num_threads=1
#     path='/Users/arya/'
#     param=['/Users/arya/batch_3.xml']
    if num_threads==1:
        results=[]
        for p in param:
            results.append(parseBatchAll(p))
    else:
        pool = multiprocessing.Pool(num_threads)
        results=pool.map(parseBatchAll,param)
        pool.terminate()
    print 'Merging...\n'
    sys.stdout.flush()
    results = mergeBipartiteBatchResultsAll(results)
    for (k,v) in results.items():
        fileout=path+'Datasets/{}.pkl'.format(k)
        pickle.dump(v,open(fileout,'wb'))
    print 'Computing Stats...\n'
    sys.stdout.flush()
    process_data_stats( data=results)

def todayRun(path='/home/arya/PubMed/Datasets/bipartite2.pkl'):
    data=pickle.load(open(path,'rb'))
    data=mergeBipartiteBatchResults(data)
    RD=data['RD']
    PD=data['PD']
    geo= RD['PDB']
    print geo
    from collections import Counter
    hist= map(lambda (k,v): v, Counter(geo).items())
    import pylab as plt
    plt.hist(hist, normed=1, histtype='stepfilled')
    print hist
def word_cloud():    
    from os import path
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    
    d = path.dirname(__file__)
    
    # Read the whole text.
    text = """The wordcloud library is MIT licenced, but contains DroidSansMono.ttf, a true type font by Google, that is apache licensed. The font is by no means integral, and any other font can be used by setting the font_path variable when creating a WordCloud object.
    """
    wordcloud = WordCloud(background_color="white",max_words=20).generate(text)
    # Open a plot of the generated image.
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)


    
if __name__ == '__main__':
    from time import time
    s=time()
    parseAll(runname='fromGEOandPubMed')
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)
