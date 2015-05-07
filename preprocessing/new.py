#!/usr/bin/env python
import pylab as P
import sys;
import re;
from DBUtil import *
import string

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

def get_BoW(corpus):
    Abs, DT, dic= [],[], {}
    for doc in corpus:
        dic, dt= insertToDic(dic, doc) ##  updates dictionary and creates BoW
        Abs.append(doc)
        DT.append(dt)
    
    TD={}
    for i in range(len(DT)):
        for termID,freq in DT[i].items():
            try:
                TD[termID].update({i+1:freq})
            except KeyError:
                TD[termID]={i+1:freq}
    return Abs, DT, TD, dic

def insertToDic(dic,abs):
    """
    Inserts new terms into dictionary and then returns the representation of the document
    """
    regex = re.compile(r"\b[a-z]\w+\b")
#     stopwords=get_stopwords()
#     abs=" ".join(w for w in abs.split() if not w in stopwords)
    words=regex.findall(abs)
#     words= abs.split()
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

def clean2(corpus):
    corpus[0]=corpus[0][:35]
    print corpus[0]
    print len(corpus), type(corpus)
    Abs,DT, TD, dic = get_BoW(corpus)
    print len(Abs),len(DT), len(TD), len(dic)
    TFIDF=get_corpus_tfidf(TD, DT)
    for k,v in TFIDF[0].items():
        print k,v
    exit(1)
    return abs

def clean(corpus, th =0.05):
    th=0.3
    
    print corpus[0]
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer()
    vectorizer = CountVectorizer(token_pattern=r"\b[a-z]\w+\b")
    print 'fitting...'
#     corpus = ["The sky is a blue a22 22a 11 22-33"]
    X=vectorizer.fit_transform(corpus)
    dic=vectorizer.get_feature_names()
#     for i in range(10000):
#         print i,dic[i]
    
    print '#words ',len(vectorizer.get_feature_names())
    print 'computing tfidf ...'
    from sklearn.feature_extraction.text import TfidfTransformer
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    print tfidf[0]
    exit(1)
    
    
    print 'nnz before cleaning',X.nnz
    nnz= tfidf.nonzero()
    print 'cleaning...'
    for i,j in zip(nnz[0],nnz[1]):
        if tfidf[i,j]<th:
            X[i,j]=0
    X.eliminate_zeros()
    print 'nnz after cleaning',X.nnz
    print 'extracting deleted words...'
    nnz2= X.nonzero()
    import collections
    row=  collections.Counter(nnz[0]).items()
    col=  collections.Counter(nnz[1]).items()
    row2=  collections.Counter(nnz2[0]).items()
    col2=  collections.Counter(nnz2[1]).items()
    print len(col),len(col2)
    print len(row),len(row2)
    for k,v in col2:
        if not v:
            print 'row has deleted'
    d=[]
    for k,v in col:
        if not v:
            print 'col has deleted',k
            d.append(k)
    print '# wordsto be deleted',len(d)
    exit(1)
#         print i,j ,tfidf[i,j]
    import pylab as P
    n, bins, patches = P.hist(t, 50, normed=1, histtype='stepfilled')
    P.figure()
    n, bins, patches = P.hist(t2, 50, normed=1, histtype='stepfilled')
    P.show()
    print len(t), len(t2)
    C=vectorizer.inverse_transform(X2)
    X=vectorizer.fit_transform(C)
    dic=vectorizer.get_feature_names()
    print len(vectorizer.get_feature_names())
    print 'done'
    exit(1)
    return 1




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
    if type(options) == str:
        options = options.split()
    i = 0
    param={'src':'/home/public/hctest.db','dst':'/home/public/abstracts.db','pipeline':'parse-clean', 'delete_tables':0, 'resume':False, 'R':'parse-clean', 'batchsize':5000, 'th':0}
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
        elif options[i] == '-th':
            i = i + 1
            param['th'] = float(options[i])
        i = i + 1
    import os
    if param['pipeline']=='reduce':
        param['dst']=param['src'].replace('.db', '{}.db'.format(str(param['th']).replace('.', '')))
    param['runname'] = param['pipeline']+ str(param['th']).replace('.', '')
    if not os.path.exists(param['src']):
        raise IOError('source database not found')
    
    
    if 'runname' not in param.keys():
        param['runname']=param['pipeline']
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
    print '{0} documents in corpus and {1} terms in the dictionary.'.format(N,w) , type(TD), len(TD[0]) 
    idf=[]
    i=0
    while i<w:
        idf.append(log(N / (1 + len(TD[i]))))
        i+=1
    return idf

def get_tfidf(ID, idf, DTs):
    """"
    Computes TFIDF of the Doc with ID
    """
    abs=DTs[ID]
    doc_tfidf={}
    for k in abs.keys():
        tfidf_score= tf(k,abs)*idf[k]
#         if tfidf_score > TH:
        doc_tfidf[k]=tfidf_score
    return doc_tfidf
     

def get_corpus_tfidf(TD,DT):
    n=len(DT)
    idf=get_idf(TD, n)
    
    print "Computing TFIDF..."
    TFIDF, i=[], 0
    while i<n:
        TFIDF.append(get_tfidf(i,idf,DT))
        i+=1
    return TFIDF

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

if __name__ == '__main__':
    try:
        arg=sys.argv[1:]
        arg='-src /home/arya/storage/parsed.db -dst /home/arya/clean.db  -D 1 -p clean'
        param=parse_options(arg)
        param['src']= '/home/arya/storage/parsed.db'
        param['src']= '/home/arya/parsed.db'
        with dbConnector(param) as db_conn:
            corpus=db_conn.getAll()
            corpus= map(lambda x: x[0], corpus)
            corpus[0]=corpus[0][:35]
            clean2(corpus)
    except (IOError,ValueError) as e:
        sys.stderr.write(str(e) + '\n')
        print str(e)
        with open(param['runname']+'.error', 'w') as filee:
            print >> filee, str(e)
            filee.flush()
        sys.exit(1)
        
