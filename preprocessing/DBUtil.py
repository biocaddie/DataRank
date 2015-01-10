import sqlite3;

class dbConnector():
    def __init__(self, param):
        self.log_path=param['dst'].replace('.db','.log');
        if 'clean' in param['pipeline']:
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            
            self.dst = sqlite3.connect(param['dst']);
            self.dstcur = self.dst.cursor();
            self.srccur.execute('select abs from abs where length(abs)>5');
            if param['delete_tables']:
                self.drop_tables('all')
            self.create_tables('all') 
        if 'parse' in param['pipeline']:
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            
            self.dst = sqlite3.connect(param['dst']);
            self.dstcur = self.dst.cursor();
            if param['resume']:
                self.dstcur.execute('SELECT count(*) FROM abs;') #ID is from 1..n and records is written sequentially
                last=self.dstcur.fetchone()[0]
                print 'Resuming from',last
                self.srccur.execute('SELECT ID,article_meta FROM test_parser where ID >' +str(last)+';');
            else:
                self.srccur.execute('SELECT ID,article_meta FROM test_parser');
                if param['delete_tables']:
                    self.drop_tables('all')
                self.create_tables('all')
        elif 'tfidf' in param['pipeline']:
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            self.dstcur, self.dst = self.srccur, self.src
            if param['delete_tables']:
                self.drop_tables('tfidf')
            self.create_tables('tfidf')
        elif 'reduce' in param['pipeline']:
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            self.dst = sqlite3.connect(param['dst']);
            self.dstcur = self.dst.cursor();
            if param['delete_tables']:
                self.drop_tables('all')
            self.create_tables('all')
        elif 'convertlda' in param['pipeline']:
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
    
    def drop_tables(self,tables):
        if tables=='all':
            self.dstcur.execute('drop table if exists abs;');
            self.dstcur.execute('drop table if exists dt;');
            self.dstcur.execute('drop table if exists td;');
            self.dstcur.execute('drop table if exists dic;');
        elif tables=='tfidf':
            self.dstcur.execute('drop table if exists tfidf;');

    def create_tables(self,tables):
        if tables=='all':
            self.dstcur.execute('create table abs(ID int primary key, abs text);');
            self.dstcur.execute('create table dic(ID int primary key, term text);');
            self.dstcur.execute('create table td(ID int primary key, docs text);');
            self.dstcur.execute('create table dt(ID int primary key, terms text);');
        elif tables=='tfidf':
            self.dstcur.execute('create table tfidf(ID int primary key, terms text);');
    
    def __enter__(self):
        return self;
    
    def __exit__(self, type, value, traceback):
        self.src.close();
    
    def getRawROW(self):
        return self.srccur.fetchone()
    
    def getAll(self):
        return self.srccur.fetchall()
    
    def get_dic(self,src=True):
        if src:
            self.srccur.execute('select * from dic;');
            result = self.srccur.fetchall()
        else:
            self.dstcur.execute('select * from dic;');
            result = self.dstcur.fetchall()
        dic={}
        for v,k in result:
            dic[k]=v
        return dic
    
    
    def getAbs(self):
        self.srccur.execute('SELECT * FROM abs;');
        return self.srccur.fetchall()
    
    def getTD(self):
        self.srccur.execute('SELECT * FROM td;');
        return self.srccur.fetchall()
    
    def getDT(self):
        self.srccur.execute('SELECT * FROM dt;');
        return self.srccur.fetchall()
    
    def getTFIDF(self):
        self.srccur.execute('SELECT * FROM tfidf;');
        return self.srccur.fetchall()
    
    def getNumDocs(self):
        self.srccur.execute('SELECT count(*) FROM dt');
        n1=self.srccur.fetchone()[0]
        self.srccur.execute('SELECT count(*) FROM abs');
        n2=self.srccur.fetchone()[0]
        assert n1==n2
        return n1
        
    def insertDocs_updateDic(self,IDs,Abstracts, DocsTerms, dic):
        DT={} # Document-Term Matrix for the batch
        for (ID, abs, docTerms) in zip(IDs,Abstracts, DocsTerms):
            self.dstcur.execute('INSERT INTO abs(ID, abs) VALUES (?, ?)', (ID,abs));
            self.dstcur.execute('INSERT INTO dt(ID, terms) VALUES (?, ?)', (ID,str(docTerms)));
            for termID,freq in docTerms.items():
                try:
                    DT[termID].update({ID:freq})
                except KeyError:
                    DT[termID]={ID:freq}
                     
        for termID,docs in DT.items():
                self.dstcur.execute("select docs from td where ID=?", (termID,))
                docsOfTerm= self.dstcur.fetchone()

                if docsOfTerm is None: # new term
                    rec =str(docs)
                    self.dstcur.execute('INSERT INTO td(ID, docs) VALUES (?, ?)', (termID,rec));
                else:
                    rec=str(dict(eval(docsOfTerm[0]).items()+docs.items()))
                    self.dstcur.execute("UPDATE td SET docs = ? WHERE ID= ? """,(rec,termID))
        
        if not len(dic):
            return
        self.dstcur.execute("select count(*) from dic;")
        n=self.dstcur.fetchone()[0]
        for (term,ID) in dic.items():
            if ID>=n:
                self.dstcur.execute('INSERT INTO dic(ID, term) VALUES (?, ?)', (ID,term));
        self.dst.commit();
    
    
    def insert_tfidf(self,tfidf):
        n, i=len(tfidf), 0
        while i<n:  
            self.srccur.execute('INSERT INTO tfidf(ID, terms) VALUES (?, ?)', (i+1,str(tfidf[i])));
            i+=1
        self.src.commit();
        
        
        
    def updateDic(self,dic):
        if not len(dic):
            return
        self.dstcur.execute("select count(*) from dic;")
        n=self.dstcur.fetchone()[0]
        for (term,ID) in dic.items():
            if ID>=n:
                self.dstcur.execute('INSERT INTO dic(ID, term) VALUES (?, ?)', (ID,term));
        self.dst.commit();
        
    
    def log(self, str):
        with open(self.log_path,'a') as fileout:
            print str
            print >> fileout , str
            fileout.flush()
           
        
