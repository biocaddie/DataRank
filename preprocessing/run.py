#!/usr/bin/env python
import sys;
import re;
import DBUtil as lite
import ExtractAbstract as ext
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
    from nltk.corpus import stopwords
    regex = re.compile('[%s]' % re.escape(string.punctuation))
    with open('english.stop') as file:  # http://jmlr.csail.mit.edu/papers/volume5/lewis04a/a11-smart-stop-list/english.stop
        jmlr_stopwords=file.readlines()
        for word in jmlr_stopwords:
            word=regex.sub(' ', word).split()
            for w in word:
                if w not in Dic:
                    Dic.append(w)
    Dic= list(set(Dic).union(set(stopwords.words('english'))))
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
            idx= dic.index(w)
        except ValueError:
            idx=len(dic)
            dic.append(w.lower())
        if idx in terms:
            terms[idx] += 1
        else:
            terms[idx] = 1
    return dic, terms

def get_param(argv):
    param={}
    if len(argv)==1:
        path='/home/arya/server/public/'
        param['src']=path+'hctest.db'
        param['dst']=path+'abstracts2.db'
        param['pipeline']=['clean', 'parse']
    else:
        param['src']= argv[1]
        param['dst']= argv[2]
        param['pipeline']=[argv[3:]]
    param['table_name'] = get_table_name(param['pipeline'])
    return param

def get_table_name(pipeline):
    if 'clean' in pipeline:
        return 'clean'
    if 'parse' in pipeline:
        return 'raw'
        

def main(argv):
    terms=[]
    dic=[]
    j=0
    param=get_param(argv)
    with lite.dbConnector(param) as db_conn:        
        while 1:
            j+=1
            rec=db_conn.getROW() # get a row from source database process it and insert it to destination databasr
            if rec is None:
                break
            id,doc = rec[0], rec[1]
            if 'parse' in param['pipeline']:
                id,doc = rec[0], parse(doc)
            if 'clean' in param['pipeline']:
                id,doc = rec[0], clean(doc)
            dic, terms= insertToDic(dic, doc)
            if not id%100:
                print id
            db_conn.insertDoc(id, doc ,terms)
            if j>500:
                break
        db_conn.insertDic(dic)
    print '\nDone!'
if __name__ == '__main__':
    main(sys.argv);