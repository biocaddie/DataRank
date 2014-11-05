#!/usr/bin/env python
import sys;
import re;
from DBUtil import *
import string

def parse(doc):
    """
    Extracts abstract and ignores the tags extra white spaces within abstracts.
    """
    doc=doc[doc.find('<abstract>'): doc.find('</abstract>')]
    doc= re.sub('<[^>]*>', '', doc[doc.find('<abstract>'): doc.find('</abstract>')])
    doc= re.sub('[\n\t]', '', doc)
    doc= re.sub('\s+', ' ', doc).encode('ascii', errors='backslashreplace').lower()
    return doc

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
    
def clean(doc):
    regex = re.compile('[%s\d]' % re.escape(string.punctuation))
    stopwords=get_stopwords()
    doc=" ".join(w for w in doc.split() if not w in stopwords)
    doc=regex.sub(' ', doc)
    doc= re.sub('\s+', ' ', doc)
    from stemming.porter2 import stem
    doc = " ".join([stem(word) for word in doc.split(" ")])

    return doc

def insertToDic(dic,doc):
    """
    Inserts new terms into dictionary and then returns the representation of the document
    """
    words= doc.split()
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
    param={'src':'/home/public/hctest.db','dst':'/home/public/abstracts.db','pipeline':'parse-clean', 'delete_tables':0, 'r':0, 'R':'parse-clean', 'batchsize':250}
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
            i = i + 1
            param['resume'] = int(options[i])
        elif options[i] == '-b':
            i = i + 1
            param['batchsize'] = int(options[i])
        i = i + 1
    import os
    if not os.path.exists(param['src']):
        raise IOError('source database not found')
    
    
    param['table_name'] = get_table_name(param['pipeline'])
    if 'runname' not in param.keys():
        param['runname']=param['table_name']
    return param
    

def tf(word, doc):
    n=float(sum(doc.values())) # # of words
    try:
        f=doc[word]
    except KeyError:
        f=0
    return f / n

def get_idf(TD,DT):
    from math import log
    N, w=len(DT), len(TD)
    print '{0} documents in corpus and {1} terms in the dictionary.'.format(N,w)
    idf=[]
    i=0
    while i<w:
        
        idf.append(log(N / (1 + len(eval(TD[i][1])))))
        i+=1
    return idf

def get_tfidf(id, idf, DT, TH):
    doc=eval(DT[id][1])
    doc_tfidf={}
    print doc
    for k in doc.keys():
        tfidf_score= tf(k,doc)*idf[k]
        print k, tfidf_score
        if tfidf_score > TH:
            doc_tfidf[k]=tfidf_score
            print k, tfidf_score,doc_tfidf
    print doc_tfidf
    exit(1)
    return doc_tfidf
     
def get_corpus_tfidf(db_conn,th):
    TD=db_conn.getTD() 
    DT=db_conn.getDT()
    idf=get_idf(TD, DT)
    DT_tfidf, i, N=[], 0, len(DT)
    while i<N:
        DT_tfidf.append(get_tfidf(i,idf,DT, th))
        i+=1
    return DT_tfidf

def get_table_name(pipeline):
    if 'tfidf' in pipeline:
        return 'tfidf'
    if 'clean' in pipeline:
        return 'clean'
    if 'parse' in pipeline:
        return 'raw'
    
if __name__ == '__main__':
    def exit_with_help():
        print("""\
Usage: preprocess.py [options] 
options :
-src {source database path} (default /home/public/hctest.db)
-dst {destination database path} (default /home/public/abstracts.db)
-D {0,1}: deletes tables if they exit (default 0)
-r {0,1} : resume from the last record inserted (default 0) 
-p {parse, parse-clean, tfidf} process pipeline (default parse-clean) 
-R {runname}  (default process pipeline)
-th {threshold for tfidf} (default 0)
-b {batchsize} (default 250)
""")

    if len(sys.argv) < 2:
        exit_with_help()
    options = sys.argv[1:]
    try:
        param=parse_options(options)
        with dbConnector(param) as db_conn:
            if param['pipeline']=='tfidf':
                tfidf=get_corpus_tfidf(db_conn,param)
                db_conn.insert_tfidf(tfidf)
            else:
                terms_of_doc, dic, j={}, {}, 0
                db_conn.log( 'Docs Processed\tDic Size')
                while 1:
                    Docs, DocTerms, IDs=[],[], []
                    j+=1
                    rec=db_conn.getRawROW() # get a row from source database process it and insert it to destination database
                    if rec is None:
                        break
                    id,doc = rec[0], rec[1]
                    if 'parse' in param['pipeline']:
                        id,doc = rec[0], parse(doc)
                    if 'clean' in param['pipeline']:
                        id,doc = rec[0], clean(doc)
                    dic, terms_of_doc= insertToDic(dic, doc)
                    if not id%param['batchsize']:
                        db_conn.log( '{0}\t{1}'.format(id,len(dic)))
                        db_conn.insertDocs(IDs, Docs ,DocTerms)
                        db_conn.updateDic(dic)
                db_conn.log( '{0}\t{1}'.format(id,len(dic)))
                db_conn.insertDocs(IDs, Docs ,DocTerms)
                db_conn.updateDic(dic)
    except (IOError,ValueError) as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
        
#         -src /home/arya/abstracts.db -p tfidf -D 1