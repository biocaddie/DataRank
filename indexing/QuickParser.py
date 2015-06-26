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


def getDatasets(pmid,article,PD,RD):
    if 'DataBankList' not in article.keys() : return PD,RD
    dblist =article['DataBankList']
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


def getMeSH(rec):
    try:
        mesh=[]
        for item in rec['MeshHeadingList']:
            mesh.append(item['DescriptorName'].attributes['UI'])
        return mesh
    except:
        return None        

def getDOI(record):
    article=record['MedlineCitation']['Article']
    if 'ELocationID' in article.keys():
        for doi in article['ELocationID']:
            if doi.__dict__['attributes'][u'EIdType']==u'doi'and doi.__dict__['attributes'][u'ValidYN']==u'Y':
                return unicode(doi)
    if 'PubmedData' in record.keys():
        if 'ArticleIdList' in record[u'PubmedData'].keys(): 
            for item in record[u'PubmedData'][u'ArticleIdList']:
                if item.__dict__['attributes'][u'IdType']==u'doi':
                    return unicode(item)
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

def parseBatch(path):
    batch = {'PJournal':{}, 'PDate':{}, 'PAbstract':{},'PData':{},'RData':{},'PAuthor':{},'PMeSH':{},'PLanguage':{}, 'PDOI':{}, 'PTitle':{}}
    f=open(path)
#     f = Entrez.efetch(db='pubmed',id='10540283', retmode="xml")
#     f = Entrez.efetch(db='pubmed',id='19897313', retmode="xml")
    records = Entrez.parse(f)
    try:
        for record in records:
            if 'MedlineCitation' in record.keys():
                rec=record['MedlineCitation']
                pmid=str(rec['PMID'])
                batch['PMeSH'][pmid]=getMeSH(rec)
                batch['PJournal'][pmid]={'jid':getJID(rec), 'jname':getJname(rec)}
                if 'Article' in rec.keys():
                    article=rec['Article']
                    batch['PData'],batch['RData']=getDatasets(pmid, article , batch['PData'],batch['RData'])
                    batch['PAbstract'][pmid]    = getAbstract(article)
                    batch['PDate'][pmid]        = {'year':getYear(article),'month':getMonth(article)}
                    batch['PAuthor'][pmid]      =getAuthor(article)
                    batch['PLanguage'][pmid]    =getLanguage(article)
                    batch['PDOI'][pmid]         = getDOI(record)
                    batch['PTitle'][pmid]       = getTitle(article)
    except:
        print >> sys.stderr, '{}\n{}\n***********'.format(path,traceback.format_exc())
    print path 
    sys.stdout.flush()
    pickle.dump(batch, open(path.replace('.xml','.pkl'),'wb'))

def process_data_stats(path=None):
    data=pickle.load(open(path))
#     with open(path.replace('.pkl','.log'),'a') as f:
    print  '************************************************'
    print  '{:20}{:10}{:10}'.format('Repository','#Datasets', '#Uniques')
    rd = sorted(map(lambda (k,v): (k,len(v),len(set(v))),data['RD'].items()),key=lambda x: x[1],reverse=True)
    for [k,u,v] in rd:    print  '{:20}{:10}{:10}'.format(k,u,v)
    print  '-------------------------------\n{:20}{:10}{:10}\n'.format('Total',sum(map(lambda (k,u,v):u,rd)),sum(map(lambda (k,u,v):v,rd)))
    print  'Until Batch {:5}, {:7} datasets are found {:7} papers'.format(data['iter'], sum(map(len,data['PD'].values())),len(data['PD'].keys()))

def mergeBatchResults(path):
    P,PD,RD,PA,PM,PL, PDOI, PT={},{},{},{},{},{},{}, {}
    for batch in None:
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
    for (k,v) in None.items():
        fileout=path+'Datasets/{}.pkl'.format(k)
        pickle.dump(v,open(fileout,'wb'))




def parse(runname,path='/home/arya/PubMed/',num_threads=5):
    num_batches = max(map(lambda x: int(x.split('_')[1].split('.')[0]),[ f for f in os.listdir(path+'MEDLINE/raw/') if os.path.isfile(os.path.join(path+'MEDLINE/raw/',f)) ]))+1
    fileout=path+'Datasets/{}.pkl'.format(runname)
    sys.stdout = open(fileout.replace('.pkl','.log'),'w')
    sys.stderr = open(fileout.replace('.pkl','.err'),'w')
    start=0
    param=[path+'MEDLINE/raw/batch_{}.xml'.format(j) for j in range(start, num_batches)]
    
    if num_threads==1:
        for p in param: 
            parseBatch(p)
    else:
        multiprocessing.Pool(num_threads).map(parseBatch,param)
def get_all_files_in_dir(path):
    return [ path+f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]

def  merge(path='/home/arya/PubMed/'):
    files =[f for f in get_all_files_in_dir(path+'MEDLINE/raw/') if f[-4:]=='.pkl']
    relations=pickle.load(open(path+'MEDLINE/raw/batch_0.pkl','rb')).keys()
    print 'Merging', relations
    for relation in relations:
        sys.stdout = open('{}Datasets/merge_{}.log'.format(path,relation),'w')
        sys.stderr = open('{}Datasets/merge_{}.err'.format(path,relation),'w')
        all_batches={}
        for j in range(len( files)):
            batch=pickle.load(open(files[j],'rb'))[relation]
            print j,files[j],len(batch), sys.stdout.flush()
            if relation != 'RData' :
                all_batches.update(batch)
            else:
                for k,v in batch.items():
                    if k in all_batches.keys():
                        for i in v:
                            all_batches[k].append(i)
                    else:
                        all_batches[k]=v
        pickle.dump(all_batches,open('{}Datasets/{}.pkl'.format(path,relation),'wb'))

def word_cloud():    
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    text = """The wordcloud library is MIT licenced, but contains DroidSansMono.ttf, a true type font by Google, that is apache licensed. The font is by no means integral, and any other font can be used by setting the font_path variable when creating a WordCloud object.
    """
    wordcloud = WordCloud(background_color="white",max_words=20).generate(text)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)
    
    
if __name__ == '__main__':
    from time import time
    s=time()
#     parse(runname='parseAll')
    merge()
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)
