#!/usr/bin/env python
import sys;
import re;
from preprocessing import DBUtil as lite
from preprocessing import ExtractAbstract as ext

def parse(doc):
    doc=doc[doc.find('<abstract>'): doc.find('</abstract>')]
    doc= re.sub('<[^>]*>', '', doc[doc.find('<abstract>'): doc.find('</abstract>')])
#     doc= re.sub('[\n\t&#]', '', doc)
    doc= re.sub('[\n\t]', '', doc)
    doc= re.sub('\s+', ' ', doc).encode('ascii', errors='backslashreplace').lower()
    return doc

def clean(doc):
    import string
    doc=''.join([i for i in doc if not i.isdigit()])
    exclude = set(string.punctuation)
    doc = ''.join(ch for ch in doc if ch not in exclude)
    return doc

def insertDic(dic,doc):
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

def main(argv):
    terms=[]
    dic=[]
    j=0
    print len(argv)
    if len(argv)==1:
        path='/home/arya/abstracts.db'
    else:
        path= argv[1]
    process='clean'
    with lite.dbConnector(path,process) as db_conn:        
        while 1:
            j+=1
            rec=db_conn.getROW()
            if rec is None:
                break
            print rec
            if process == 'raw':
                id,doc = rec[0], parse(rec[1])
            else:
                id,doc = rec[0], clean(rec[1])
            print doc
            dic, terms= insertDic(dic, doc)
            if not id%100:
                print id
            db_conn.insertDoc(id, doc ,terms)
            if j>1:
                break
        db_conn.insertDic(dic)
    print 'Done'
if __name__ == '__main__':
    main(sys.argv);