import sqlite3;

class dbConnector():
    def __init__(self, param):
        self.run_name=param['runname'];
        if 'clean' in param['pipeline'] or 'parse' in param['pipeline']:
            self.table_name=param['table_name'];
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            
            self.dst = sqlite3.connect(param['dst']);
            self.dstcur = self.dst.cursor();
            if param['resume']:
                self.dstcur.execute('SELECT count(*) FROM abs_{0}'.format(self.table_name)); #ID is from 1..n and records is written sequentially
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
            self.table_name='tfidf'+str(param['th']).replace('.', '');
            if param['delete_tables']:
                self.drop_tables('all')
            self.create_tables('all')
        elif 'reduce' in param['pipeline']:
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            self.dstcur, self.dst = self.srccur, self.src
            self.table_name='reduced'+str(param['th']).replace('.', '');
            if param['delete_tables']:
                self.drop_tables('all')
            self.create_tables('all')
    
    def drop_tables(self,tables):
        if tables=='all':
            self.dstcur.execute('drop table if exists abs_'+self.table_name+';');
            self.dstcur.execute('drop table if exists dt_'+self.table_name+';');
            self.dstcur.execute('drop table if exists td_'+self.table_name+';');
            self.dstcur.execute('drop table if exists dic_'+self.table_name+';');
        elif tables=='tfidf':
            self.dstcur.execute('drop table if exists dt_'+self.table_name+';');

    def create_tables(self,tables):
        if tables=='all':
            self.dstcur.execute('create table abs_'+self.table_name+'(ID int primary key, abs text);');
            self.dstcur.execute('create table dic_'+self.table_name+'(ID int primary key, term text);');
            self.dstcur.execute('create table td_'+self.table_name+'(ID int primary key, docs text);');
            self.dstcur.execute('create table dt_'+self.table_name+'(ID int primary key, terms text);');
        elif tables=='tfidf':
            self.dstcur.execute('create table dt_'+self.table_name+'(ID int primary key, terms text);');
    
    def __enter__(self):
        return self;
    
    def __exit__(self, type, value, traceback):
        self.src.close();
    
    def getRawROW(self):
        return self.srccur.fetchone()
    
    def get_dic(self, table_name=None):
        if table_name is None:
            table_name=self.table_name
        self.dstcur.execute('select * from dic_'+table_name +';');
        result = self.dstcur.fetchall()
        dic={}
        for v,k in result:
            dic[k]=v
        return dic
    
    
    def getAbs(self,table_name=None):
        if table_name==None:
            table_name=self.table_name
        self.srccur.execute('SELECT * FROM abs_'+table_name);
        return self.srccur.fetchall()
    
    def getTD(self,table_name=None):
        if table_name==None:
            table_name=self.table_name
        self.srccur.execute('SELECT * FROM td_'+table_name);
        return self.srccur.fetchall()
    
    def getDT(self,table_name=None):
        if table_name==None:
            table_name=self.table_name
        self.srccur.execute('SELECT * FROM dt_'+table_name);
        return self.srccur.fetchall()
    
    def getNumDocs(self):
        self.srccur.execute('SELECT count(*) FROM dt_clean');
        n1=self.srccur.fetchone()[0]
        self.srccur.execute('SELECT count(*) FROM abs_clean');
        n2=self.srccur.fetchone()[0]
        assert n1==n2
        return n1
        
    def insertDocs_updateDic(self,IDs,Abstracts, DocsTerms, dic):
        DT={} # Document-Term Matrix for the batch
        for (ID, abs, docTerms) in zip(IDs,Abstracts, DocsTerms):
            self.dstcur.execute('INSERT INTO abs_'+self.table_name+'(ID, abs) VALUES (?, ?)', (ID,abs));
            self.dstcur.execute('INSERT INTO dt_'+self.table_name+'(ID, terms) VALUES (?, ?)', (ID,str(docTerms)));
            for termID,freq in docTerms.items():
                try:
                    DT[termID].update({ID:freq})
                except KeyError:
                    DT[termID]={ID:freq}
                     
        for termID,docs in DT.items():
                self.dstcur.execute("select docs from td_"+self.table_name+" where ID=?", (termID,))
                docsOfTerm= self.dstcur.fetchone()

                if docsOfTerm is None: # new term
                    rec =str(docs)
                    self.dstcur.execute('INSERT INTO td_'+self.table_name+'(ID, docs) VALUES (?, ?)', (termID,rec));
                else:
                    rec=str(dict(eval(docsOfTerm[0]).items()+docs.items()))
                    self.dstcur.execute("UPDATE td_"+self.table_name+" SET docs = ? WHERE ID= ? """,(rec,termID))
        
        if not len(dic):
            return
        self.dstcur.execute("select count(*) from dic_"+self.table_name+";")
        n=self.dstcur.fetchone()[0]
        for (term,ID) in dic.items():
            if ID>=n:
                self.dstcur.execute('INSERT INTO dic_'+self.table_name+'(ID, term) VALUES (?, ?)', (ID,term));
        self.dst.commit();
    
    
    def insert_tfidf(self,tfidf):
        n, i=len(tfidf), 0
        while i<n:  
            self.srccur.execute('INSERT INTO dt_'+self.table_name+'(ID, terms) VALUES (?, ?)', (i+1,str(tfidf[i])));
            i+=1
        self.src.commit();
        
        
        
    def updateDic(self,dic):
        if not len(dic):
            return
        self.dstcur.execute("select count(*) from dic_"+self.table_name+";")
        n=self.dstcur.fetchone()[0]
        for (term,ID) in dic.items():
            if ID>=n:
                self.dstcur.execute('INSERT INTO dic_'+self.table_name+'(ID, term) VALUES (?, ?)', (ID,term));
        self.dst.commit();
        
    
    def log(self, str):
        with open(self.run_name+'.log','a') as fileout:
            print >> fileout , str
            fileout.flush()
           
        
