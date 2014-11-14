#!/usr/bin/env python
import sys;
import re;
from DBUtil import *
import string

def parse(abs):
    """
    Extracts abstract and ignores the tags extra white spaces within abstracts.
    """
    abs=abs[abs.find('<abstract>'): abs.find('</abstract>')]
    abs= re.sub('<[^>]*>', '', abs[abs.find('<abstract>'): abs.find('</abstract>')])
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
    regex = re.compile('[%s\d]' % re.escape(string.punctuation))
    stopwords=get_stopwords()
    abs=" ".join(w for w in abs.split() if not w in stopwords)
    abs=regex.sub(' ', abs)
    abs= re.sub('\s+', ' ', abs)
    from stemming.porter2 import stem
    abs = " ".join([stem(word) for word in abs.split(" ")])

    return abs

def insertToDic(dic,abs):
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
    
    
    param['table_name'] = get_table_name(param['pipeline'])
    if 'runname' not in param.keys():
        param['runname']=param['table_name']
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

def get_tfidf(ID, idf, DTs, TH):
    """"
    Computes TFIDF of the Doc with ID
    """
    abs=eval(DTs[ID][1])
    doc_tfidf={}
    for k in abs.keys():
        tfidf_score= tf(k,abs)*idf[k]
        if tfidf_score > TH:
            doc_tfidf[k]=tfidf_score
    return doc_tfidf
     
def get_corpus_tfidf(db_conn,th):
    print "Computing IDF..."
    n=db_conn.getNumDocs()
    M=db_conn.getTD() 
    idf=get_idf(M, n)
    
    print "Computing TFIDF..."
    M=db_conn.getDT()
    DT_tfidf, i=[], 0
    while i<n:
        DT_tfidf.append(get_tfidf(i,idf,M, th))
        i+=1
    return DT_tfidf

def reduce_to_th(db_conn,param):
    dic={}
    dic_old=db_conn.get_dic('clean')
    dic_old_inverse = {value: key for (key, value) in dic_old.items()}
    Abstracts, DTs, IDs=[],[], [] # Buffer
    DTs_tfidf=db_conn.getDT('tfidf'+str(param['th']).replace('.', ''))
    DTs_clean=db_conn.getDT('clean')
    Abstracts_clean=db_conn.getAbs('clean')
    for (abs_clean, dt_clean, dt_tfidf) in zip(Abstracts_clean, DTs_clean, DTs_tfidf):
        ID,dt_clean, id1,dt_tfidf, id2, abs_clean = dt_clean[0],dt_clean[1], dt_tfidf[0], dt_tfidf[1], abs_clean[0], abs_clean[1] 
        assert ID ==id1 and ID == id2
        dt_clean, dt_tfidf=eval(dt_clean),eval(dt_tfidf)
        removeIDs=list(set(dt_clean.keys()) - set(dt_tfidf.keys()))
        remove =[dic_old_inverse[termID] for termID in removeIDs]
        abs_tfidf=abs_clean
        for t in remove:
            abs_tfidf=abs_tfidf.replace(t,'')
        abs_tfidf=abs_tfidf.replace('  ',' ').strip()
        dic, dt_tfidf= insertToDic(dic, abs_tfidf)
        IDs.append(ID)
        Abstracts.append(abs_tfidf)
        DTs.append(dt_tfidf)
        if not ID%param['batchsize']:
            db_conn.log( '{0}\t{1}'.format(ID,len(dic)))
            db_conn.insertDocs_updateDic(IDs, Abstracts ,DTs, dic)
            Abstracts, DTs, IDs=[],[], []  # Releasing buffer
    db_conn.log( '{0}\t{1}\nDone!'.format(ID,len(dic)))
    db_conn.insertDocs_updateDic(IDs, Abstracts ,DTs,dic)
    return

def get_table_name(pipeline):
    if 'reduce' in pipeline:
        return 'reduce'
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
                tfidf=get_corpus_tfidf(db_conn,param['th'])
                db_conn.insert_tfidf(tfidf)
            elif param['pipeline']=='reduce':
                reduce_to_th(db_conn,param)
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
                db_conn.log( '{0}\t{1}\nDone!'.format(ID,len(dic)))
                db_conn.insertDocs_updateDic(IDs, Abstracts ,DTs,dic)
    except (IOError,ValueError) as e:
        sys.stderr.write(str(e) + '\n')
        with open(param['runname']+'.error', 'w') as filee:
            print >> filee, str(e)
            filee.flush()
        sys.exit(1)
        