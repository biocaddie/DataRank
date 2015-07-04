'''
Created on Jun 19, 2015

@author: arya
'''
import pickle,sys,multiprocessing,os
import traceback
from Bio import Entrez
import pandas as pd
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
            author=(None,None,None)
            try:
                author[0]=item['ForeName']
            except:
                pass
            try:
                author[1]=item['LastName']
            except:
                pass
            try:
                author[2]=item['Initials']
            except:
                pass
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
    batch = {'P':{},'PD':{},'RD':{},'PA':{},'PM':{},'PL':{}}
    f=open(path)
    records = Entrez.parse(f)
    try:
        for record in records:
            if 'MedlineCitation' in record.keys():
                rec=record['MedlineCitation']
                pmid=str(rec['PMID'])
                batch['PM'][pmid]=getMeSH(rec)
                if 'Article' in rec.keys():
                    article=rec['Article']
                    batch['PD'],batch['RD']=getDatasets(pmid, article , batch['PD'],batch['RD'])
                    batch['PA'][pmid]      =getAuthor(article)
                    batch['PL'][pmid]    =getLanguage(article)
                    batch['P'][pmid]       = [getTitle(article), getYear(article), getMonth(article),getDOI(record), getAbstract(article), getJID(rec), getJname(rec)]
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


def parseMEDLINE(path,num_threads=15):
    num_batches = max(map(lambda x: int(x.split('_')[1].split('.')[0]),[ f for f in os.listdir(path+'MEDLINE/raw/') if os.path.isfile(os.path.join(path+'MEDLINE/raw/',f)) ]))+1
    fileout=path+'Log/parseMEDLINE.pkl'
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

def  mergeMEDLINE(path):
    files =[f for f in get_all_files_in_dir(path+'MEDLINE/raw/') if f[-4:]=='.pkl']
    relations=pickle.load(open(path+'MEDLINE/raw/batch_0.pkl','rb')).keys()
    if not os.path.exists(path+'Log'):            os.makedirs(path+'Log')
    sys.stdout = open('{}Log/mergeMEDLINE.log'.format(path),'w')
    sys.stderr = open('{}Log/mergeMEDLINE.err'.format(path),'w')
    print 'Merging', relations
    for relation in relations:
        print relation
        All={}
        for j in range(len( files)):
            try:
                batch=pickle.load(open(files[j],'rb'))[relation]
                print j,files[j],len(batch), sys.stdout.flush()
                if relation != 'RD' :
                    All.update(batch)
                else:
                    for k,v in batch.items():
                        if k in All.keys():
                            for i in v:
                                All[k].append(i)
                        else:
                            All[k]=v
            except:
                print >> sys.stderr, files[j]
        if relation == 'PA':
            All=pd.DataFrame(convertDicofListofTuples_listofTuples(All),columns=('pmid','name','family','initial'))
        elif relation in ['RD','PD', 'PL', 'PM' ]:
            All=pd.DataFrame(convertDicofList_listofTuples(All))
        elif relation =='P':
            All=pd.DataFrame(All).transpose()
            All.columns=('title','year','month','doi','abstract','jid','jname')
            All.index.name='pmid'
        else:
            print >> sys.stderr , 'No ralation named', relation
            exit()
        All.to_pickle('{}Datasets/{}.df'.format(path,relation)) 

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

def convertDicofListofTuples_listofTuples(dic):
    tuples=[]
    for k,V in dic.items(): # dictionary of lists of tuples
        if V:
            for v in V:
                tuples.append((k,)+v)
    return tuples

def convertDicofList_listofTuples(dic):
    tuples=[]
    for k,V in dic.items(): # dictionary of lists of tuples
        if V:
            for v in V:
                tuples.append((k,v))
    return tuples

def parseMeSH(path='/home/arya/PubMed/MeSH/desc2015.xml'):
    from ParseMeSHXML import parse_mesh 
    from MEDLINEDatabase import MeSHDB
    records=parse_mesh(path)
    db=MeSHDB()
    for r in records:
        db.mesh.id.append(r.ui)
        db.mesh.name.append(r.name)
        for c in r.concepts:
            db.concept.id.append(c.ui)
            db.concept.name.append(c.name)
            for t in c.terms:
                db.entryTerm.name.append(t.name)
                db.entryTerm.id.append(t.ui)
    pickle.dump(db,open(path.replace('.xml','.pkl'),'wb'))
    M={'uid':db.mesh.id,'name':db.mesh.name}
    pickle.dump(M,open(path.replace('desc2015.xml','mesh.pkl'),'wb'))
    M=pickle.load(open('/home/arya/PubMed/MeSH/mesh.pkl'))
    M=pd.DataFrame(M)
    M['mid']=M.index
    M.index=M.uid    
    print 'MeSH Dictionary has {} terms ({} are distinct)'.format(M.uid.shape[0], M.uid.unique().shape[0])
    M.drop('uid',axis=1,inplace=True)
    M.to_pickle('/home/arya/PubMed/GEO/Datasets/M.df')
    return db    


if __name__ == '__main__':
    from time import time
    s=time()
    path='/home/arya/PubMed/GEO/'
    parseMeSH()
    parseMEDLINE(path)
    mergeMEDLINE(path)
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)





