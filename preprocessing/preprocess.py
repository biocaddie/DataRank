#!/usr/bin/env python
from sklearn.feature_extraction.text import CountVectorizer
from stemming.porter2 import stem
import os
import sys;
import re;
import collections
from DBUtil import *
import pylab as P
import string
from numpy import array, ones, nonzero
import Stemmer #PyStemmer
english_stemmer = Stemmer.Stemmer('en')
db_conn=0
min_doc_length=5
def parse(abs):
    """
    Extracts abstract and ignores the tags extra white spaces within abstracts.
    """
    try:
        s=re.search(r'<abstract[^>]*>', abs).end()
        e=re.search(r'<[^>]*/abstract>', abs).start()
    except AttributeError:
        return ''
    abs=abs[s:e]
    abs= re.sub('<[^>]*>', '', abs)
    abs= re.sub('[\n\t]', '', abs)
    abs= re.sub('\s+', ' ', abs).encode('ascii', errors='backslashreplace').lower()
    return abs

def get_stopwords():
    Dic=[]

    regex = re.compile('[%s]' % re.escape(string.punctuation))
    with open('english.stop') as file:  # http://jmlr.csail.mit.edu/papers/volume5/lewis04a/a11-smart-stop-list/english.stop
        jmlr_stopwords=file.readlines()
        for word in jmlr_stopwords:
            word=regex.sub(' ', word).split()
            for w in word:
                if w not in Dic:
                    Dic.append(w)
#     from nltk.corpus import stopwords   ## JMLR stopwords is a superset of nltk
#     Dic= list(set(Dic).union(set(stopwords.words('english'))))
    return Dic
    
def clean_old(abs):
    regex = re.compile('[%s\d]' % re.escape(string.punctuation)) # to keep numbers just remove \d
    stopwords=get_stopwords()
    abs=" ".join(w for w in abs.split() if not w in stopwords)
    abs=regex.sub(' ', abs)
    abs= re.sub('\s+', ' ', abs) #remove white spaces
#     abs = " ".join([stem(word) for word in abs.split(" ")])
    return abs

class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
         analyzer = super(CountVectorizer, self).build_analyzer()
         return lambda doc: english_stemmer.stemWords((analyzer(doc)))


def tfidf_th(X,th):
    print 'computing tfidf ...'
    from sklearn.feature_extraction.text import TfidfTransformer
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)

    nz= tfidf.nonzero()
    print 'cleaning...'
    for i,j in zip(nz[0],nz[1]):
        if tfidf[i,j]<th:
            X[i,j]=0
    X.eliminate_zeros()
    return X

def inverse_index(IDX,idx):
    inv_idx= -ones(len(IDX))
    for i in range(len(idx)):
        inv_idx[idx[i]]=i
    return inv_idx

def remove_low_freq_words(X,th=3):
    print 'Removing low freq words... (' ,
    nz= X.nonzero()
    word_freq=  map(lambda x: x[1], collections.Counter(nz[1]).items())
    to_remove=[]
    for i in range(len(word_freq)):
        if word_freq[i]<=th:
            to_remove.append(i)
    to_remove=set(to_remove)
    print len(to_remove), 'will be removed )'
    for i,j in zip(nz[0],nz[1]):
        if j in to_remove:
            X[i,j]=0
    X.eliminate_zeros()
    return X
    
def clean(corpus, param):
#     param['do_stemming']=True
    db_conn.log( 'Cleaning: {}   Min TF={}   Min TFIDF={}'.format(('Not','')[param['do_stemming']] + 'Stemming', param['thtf'], param['thtfidf'] ))
    out_path = param['dst'].replace('.db','')
    
    if param['do_stemming']:
        vectorizer = StemmedCountVectorizer(min_df=1,stop_words='english', analyzer='word', ngram_range=(1,1),token_pattern=r"\b[a-z]\w+\b")
    else:
        vectorizer = CountVectorizer(min_df=1,stop_words='english', analyzer='word', ngram_range=(1,1),token_pattern=r"\b[a-z]\w+\b")
        
    db_conn.log( 'Creating BoW...')
    X=vectorizer.fit_transform(corpus)
    dic=array(vectorizer.get_feature_names())
#     writeDic(dic,path='/home/arya/bigdata/pmc/pmc.full')
    term_idx_all=range(len(dic))
    iiii= corpus_stats(X)
    for (i,j) in zip(term_idx_all,iiii):
        if i!=j:
            print i,j
    
    if param['thtfidf']>0:
        X=tfidf_th(X,param['thtfidf'])
        term_idx_clean=corpus_stats(X)
    
    if param['compute_tfidf']:
        print 'computing tfidf ...'
        from sklearn.feature_extraction.text import TfidfTransformer
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(X)
        
    
    X=remove_low_freq_words(X,param['thtf'])
    term_idx_clean=corpus_stats(X)
    
    inv_idx_full2clean = inverse_index(term_idx_all, term_idx_clean)
    removed=list(set(range(len(dic)))-set(term_idx_clean))
    removed = dic[removed]
    writeBoW(X, inv_idx_full2clean, out_path)
    writeBoW(tfidf, inv_idx_full2clean, out_path, tfidf= True)
    writeDic(dic[term_idx_clean],out_path)
     

def corpus_stats(X, do_plot=False):
#     P.ion()
    nz= X.nonzero()
    
    
    doc_lengths= map(lambda x: x[1], collections.Counter(nz[0]).items()) # lengths of docs in the corpus nz[0] rows of nonzero elemenrs
    doc_ids= map(lambda x: x[0], collections.Counter(nz[0]).items())
    
    term_idfs=  map(lambda x: x[1], collections.Counter(nz[1]).items()) # number of happenings of terms in different docs
    term_ids=  map(lambda x: x[0], collections.Counter(nz[1]).items())
    db_conn.log( 'There are {} docs with {} words and dic size of {} '.format(len(doc_ids),X.nnz, len(term_ids)))
    if do_plot:
        P.figure()
        P.subplot(1,2,1)
        n, bins, patches = P.hist(doc_lengths, max(doc_lengths),  histtype='stepfilled')
        P.title('Document lenghths')
        P.subplot(1,2,2)
        P.title('Word Frequency')
        n, bins, patches = P.hist(term_idfs, max(term_idfs),  histtype='stepfilled')
        P.show()
    return term_ids


def insertToDic(dic,abs):
    """
    Inserts new terms into dictionary and then returns the representation of the document
    """
    words= abs.split()
    DT={}
    for w in words:
        w=w.lower()
        try:
            idx= dic[w]
        except KeyError:
            idx=len(dic)
            dic[w.lower()]=idx
        if idx in DT:
            DT[idx] += 1
        else:
            DT[idx] = 1
    return dic, DT

def insertToReducedDic(dic, dic_old, abs):
    """
    Inserts new terms into dictionary and then returns the representation of the document
    """
    words= abs.split()
    terms={}
    
    for w in words:
        w=w.lower()
        try:
            idx= dic[w]
        except KeyError:
            idx=len(dic)
            dic[w.lower()]=idx
        if idx in terms:
            terms[idx] += 1
        else:
            terms[idx] = 1
    return dic, terms
   

def parse_options(options):
    print options
    if type(options) == str:
        options = options.split()
    i = 0
    param={'src':'/home/public/hctest.db','pipeline':'parse-clean', 'compute_tfidf':False, 'delete_tables':1, 'resume':False, 'R':'parse-clean', 'batchsize':5000, 'thtfidf':0, 'thtf':0, 'do_stemming':0}
    while i < len(options):
        if options[i] == '-src':
            i = i + 1
            param['src'] = options[i]
        elif options[i] == '-dst':
            i = i + 1
            param['dst'] = options[i]
        elif options[i] == '-p':
            i = i + 1
            param['pipeline'] = options[i]
        elif options[i] == '-D':
            i = i + 1
            param['delete_tables'] = int(options[i])
        elif options[i] == '-R':
            i = i + 1
            param['runname'] = options[i]
        elif options[i] == '-r':
            param['resume'] = True
        elif options[i] == '-b':
            i = i + 1
            param['batchsize'] = int(options[i])
        elif options[i] == '-thtf':
            i = i + 1
            param['thtf'] = int(options[i])
        elif options[i] == '-thtfidf':
            i = i + 1
            param['thtfidf'] = float(options[i])
        elif options[i] == '-tfidf':
            param['compute_tfidf'] = True
        elif options[i] == '-stm':
            i = i + 1
            param['do_stemming'] = int(options[i])
        i = i + 1
    
    if param['pipeline']=='reduce':
        param['dst']=param['src'].replace('.db', '{}.db'.format(str(param['th']).replace('.', '')))
    if param['pipeline']=='clean':
        param['dst']= param['src'].replace('.db','.clean.tf{}{}{}.db'.format(param['thtf'],('','.stemmed')[param['do_stemming']],('','.tfidf'+str(param['thtfidf']))[param['thtfidf']>0]))
	param['runname'] = param['pipeline']+ str(param['thtf']).replace('.', '')
    if not os.path.exists(param['src']):
        raise IOError('source database not found')
    
    
    if 'runname' not in param.keys():
        param['runname']=os.path.basename(param['dst'].replace('.db',''))
    return param
    

def tf(word, abs):
    n=float(sum(abs.values())) # # of words
    try:
        f=abs[word]
    except KeyError:
        f=0
    return f / n

def get_idf(TD,N):
    from math import log
    w= len(TD)
    db_conn.log( '{0} documents in corpus and {1} terms in the dictionary.'.format(N,w) )
    idf=[]
    i=0
    while i<w:
        idf.append(log(N / (1 + len(eval(TD[i][1])))))
        i+=1
    return idf

def get_tfidf(ID, idf, DTs):
    """"
    Computes TFIDF of the Doc with ID
    """
    abs=eval(DTs[ID][1])
    doc_tfidf={}
    for k in abs.keys():
        tfidf_score= tf(k,abs)*idf[k]
#         if tfidf_score > TH:
        doc_tfidf[k]=tfidf_score
    return doc_tfidf

def get_corpus_tfidf():
    db_conn.log( "Computing IDF...")
    n=db_conn.getNumDocs()
    M=db_conn.getTD() 
    idf=get_idf(M, n)
    
    db_conn.log( "Computing TFIDF...")
    M=db_conn.getDT()
    DT_tfidf, i=[], 0
    while i<n:
        DT_tfidf.append(get_tfidf(i,idf,M))
        i+=1
    return DT_tfidf

def reduce_abs(abs_old, dt_old, tfidf, dic_old_inverse,th):
    for k,v in tfidf.items():
        if v<th:
            del tfidf[k]
    IDsToRemove=list(set(dt_old.keys()) - set(tfidf.keys()))
    wordsToRemove =[dic_old_inverse[termID] for termID in IDsToRemove]
    abs=abs_old
    for t in wordsToRemove:
        abs=abs.replace(' '+t+' ',' ')
    abs=abs.replace('  ',' ').strip()
    return abs

def reduce_to_th(param):
    dic={}
    dic_old=db_conn.get_dic()
    dic_old_inverse = {value: key for (key, value) in dic_old.items()}
    Abstracts, DTs, IDs=[],[], [] # Buffer
    db_conn.log( 'Reading TFIDF')
    TFIDFs=db_conn.getTFIDF()
    db_conn.log( 'Reading DT')
    DTs_old=db_conn.getDT()
    db_conn.log( 'Reading Abs')
    Abstracts_old=db_conn.getAbs()
    db_conn.log( 'Processing')
    k,ll=0,0
    for (abs_old, dt_old, tfidf) in zip(Abstracts_old, DTs_old, TFIDFs):
        ID,dt_old, id1,tfidf, id2, abs_old = dt_old[0],eval(dt_old[1]), tfidf[0], eval(tfidf[1]), abs_old[0], abs_old[1] 
        assert ID ==id1 and ID == id2
        abs= reduce_abs(abs_old, dt_old, tfidf, dic_old_inverse, param['th'])
        dic, dt= insertToDic(dic, abs)
        IDs.append(ID)
        Abstracts.append(abs)
        DTs.append(dt)
        
        if not ID%param['batchsize']:
#             exit(1)
            db_conn.log( '{0}\t{1}\t{2}'.format(ID, len(dic), 1))
            db_conn.insertDocs_updateDic(IDs, Abstracts ,DTs, dic)
            Abstracts, DTs, IDs=[],[], []  # Releasing buffer
    db_conn.log( '{0}\t{1}\nDone!'.format(ID,len(dic)))
    db_conn.insertDocs_updateDic(IDs, Abstracts ,DTs,dic)
    return

def writeBoW_old(DTs, path='/home/arya/pmc'):
    with open(path+'.dat','w') as file:
        for id, dt in DTs:
            n=len(eval(dt))
            if n<2:
                continue
            dt= str(dt)[1:-1].replace(' ','')
            dt=dt.replace(',', ' ')
            print >> file,n,dt

def writeDic_old(dic, path='/home/arya/bigdata/pmc/pmc'):
    import operator
    dic= sorted(dic.items(), key=operator.itemgetter(1))
    with open(path+'.dic','w') as file:
        for w in dic:
            print >> file,w[0]   

def writeBoW(X, inv_idx, path='/home/arya/bigdata/pmc/pmc', tfidf=False, min_doc_length=5):
    with open(path+('.dat','.tfidf')[tfidf],'w') as file:
        nz=X.nonzero()
        for i in range(X.shape[0]):
            n=X[i].nnz
            if n<min_doc_length:
                continue
            nz=X[i].nonzero()
            dt=''
            for j in nz[1]:
                if inv_idx[j]<0:
                    continue
                dt+= ' {}:{}'.format(int(inv_idx[j]),X[i,j])
            print >> file,n,dt

def writeDic(dic, path='/home/arya/bigdata/pmc/pmc'):
    with open(path+'.dic','w') as file:
        for w in dic:
            print >> file,w   

def write_to_lda_format(param):
    DTs=db_conn.getDT()
    dic=db_conn.get_dic()
    writeBoW(DTs, param['src'].replace('.db','.dat'))
    writeDic(dic, param['src'].replace('.db','.dic'))

def exit_with_help():
        print """\
Usage: preprocess.py [options] 
options :
-src {source database path} (default /home/public/hctest.db)
-dst {destination database path} (default /home/public/abstracts.db)
-D {0,1}: deletes tables if they exit (default 1)
-r {0,1} : resume from the last record inserted (default 0) 
-p {parse, parse-clean, reduce} process pipeline (default parse-clean) 
-R {runname}  (default process pipeline)
-thtfidf {threshold for tfidf} (default 0)
-thtf {threshold for tfidf} (default 20)
-stm {0, 1}: Stemming (default 0)
-b {batchsize} (default 5000)
"""


def parse_database(param):
    DT, dic, j={}, {}, 0
    if param['resume']:
        dic=db_conn.get_dic()
    db_conn.log( '#Abstracts\t#DicWords')
    Abstracts, DTs, IDs=[],[], [] # Buffer
    while 1:
        j+=1
        record=db_conn.getRawROW() # get a row from source database process it and insert it to destination database
        if record is None:
            break
        ID,abs = record[0], record[1]
        if 'parse' in param['pipeline']:
            ID,abs = record[0], parse(abs)
#         if 'clean' in param['pipeline']:
#             ID,abs = record[0], clean(abs)
        dic, DT= insertToDic(dic, abs)
        IDs.append(ID)
        Abstracts.append(abs)
        DTs.append(DT)
        if not ID%param['batchsize']:
            db_conn.log( '{0}\t{1}'.format(ID,len(dic)))
            db_conn.insertDocs_updateDic(IDs, Abstracts ,DTs, dic)
            Abstracts, DTs, IDs=[],[], []  # Releasing buffer
            exit(1)
    db_conn.log( '{0}\t{1}\nDone!'.format(ID,len(dic)))
    db_conn.insertDocs_updateDic(IDs, Abstracts ,DTs,dic)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        exit_with_help()

    try:
        param=parse_options(sys.argv[1:])
        with dbConnector(param) as db_conn:
            if param['pipeline']=='tfidf':
                tfidf=get_corpus_tfidf()
                db_conn.insert_tfidf(tfidf)
            elif param['pipeline']=='reduce':
                param['dst']=param['src'].replace('.db', '{}.db'.format(str(param['th']).replace('.', '')))
                reduce_to_th(param)
            elif param['pipeline']=='convertlda':
                write_to_lda_format(param)
            elif param['pipeline']=='clean':
                corpus=db_conn.getAll()
                corpus= map(lambda x: x[0], corpus)
                clean(corpus,param)
            elif param['pipeline']=='parse':
                parse_database(param)
                
    except (IOError,ValueError) as e:
        print str(e)
        with open(param['runname']+'.error', 'w') as filee:
            print >> filee, str(e)
            filee.flush()
        sys.exit(1)
    print 'Done!'
        
