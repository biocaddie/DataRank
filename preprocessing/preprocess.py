#!/usr/bin/env python
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
    
def clean(abs):
    regex = re.compile('[%s\d]' % re.escape(string.punctuation)) # to keep numbers just remove \d
    stopwords=get_stopwords()
    abs=" ".join(w for w in abs.split() if not w in stopwords)
    abs=regex.sub(' ', abs)
    abs= re.sub('\s+', ' ', abs) #remove white spaces
#     from stemming.porter2 import stem
#     abs = " ".join([stem(word) for word in abs.split(" ")])
    return abs

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
    print '{0} documents in corpus and {1} terms in the dictionary.'.format(N,w)
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
     
def get_corpus_tfidf(db_conn):
    print "Computing IDF..."
    n=db_conn.getNumDocs()
    M=db_conn.getTD() 
    idf=get_idf(M, n)
    
    print "Computing TFIDF..."
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

def reduce_to_th(db_conn,param):
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

def writeBoW(DTs, path):
    with open(path+'.dat','w') as file:
        for id, dt in DTs:
            n=len(eval(dt))
            if n<2:
                continue
            dt= str(dt)[1:-1].replace(' ','')
            dt=dt.replace(',', ' ')
            print >> file,n,dt

def writeDic(dic, path):
    import operator
    dic= sorted(dic.items(), key=operator.itemgetter(1))
    with open(path+'.dic','w') as file:
        for w in dic:
            print >> file,w[0]   

def write_to_lda_format(db_conn,param):
    DTs=db_conn.getDT()
    dic=db_conn.get_dic()
    writeBoW(DTs, param['src'].replace('.db','.dat'))
    writeDic(dic, param['src'].replace('.db','.dic'))

if __name__ == '__main__':
    def exit_with_help():
        print("""\
Usage: preprocess.py [options] 
options :
-src {source database path} (default /home/public/hctest.db)
-dst {destination database path} (default /home/public/abstracts.db)
-D {0,1}: deletes tables if they exit (default 0)
-r {0,1} : resume from the last record inserted (default 0) 
-p {parse, parse-clean, reduce} process pipeline (default parse-clean) 
-R {runname}  (default process pipeline)
-th {threshold for tfidf} (default 0)
-b {batchsize} (default 5000)
""")
    param={}
    if len(sys.argv) < 2:
        exit_with_help()
    options = sys.argv[1:]
    try:
        param=parse_options(options)
        with dbConnector(param) as db_conn:
            if param['pipeline']=='tfidf':
                tfidf=get_corpus_tfidf(db_conn)
                db_conn.insert_tfidf(tfidf)
            elif param['pipeline']=='reduce':
                reduce_to_th(db_conn,param)
            elif param['pipeline']=='convertlda':
                write_to_lda_format(db_conn,param)
            else:
                DT, dic, j={}, {}, 0
                if param['resume']:
                    dic=db_conn.get_dic()
                db_conn.log( '#Abstracts\t#DicWords')
                Abstracts, DTs, IDs=[],[], [] # Buffer
                while 1:
                    j+=1
                    rec=db_conn.getRawROW() # get a row from source database process it and insert it to destination database
                    if rec is None:
                        break
                    ID,abs = rec[0], rec[1]
                    
                    if 'parse' in param['pipeline']:
                        ID,abs = rec[0], parse(abs)
                    if 'clean' in param['pipeline']:
                        ID,abs = rec[0], clean(abs)
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
    except (IOError,ValueError) as e:
        sys.stderr.write(str(e) + '\n')
        with open(param['runname']+'.error', 'w') as filee:
            print >> filee, str(e)
            filee.flush()
        sys.exit(1)
        