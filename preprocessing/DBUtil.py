import sqlite3;

class dbConnector():
    def __init__(self, param):
        if 'clean' in param['pipeline'] or 'parse' in param['pipeline']:
            self.prev_dic_size=0
            self.run_name=param['runname'];
            self.table_name=param['table_name'];
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            self.srccur.execute('SELECT id,article_meta FROM test_parser');
            self.dst = sqlite3.connect(param['dst']);
            self.dstcur = self.dst.cursor();
            if param['delete_tables']:
                self.dstcur.execute('drop table if exists abs_'+self.table_name+';');
                self.dstcur.execute('drop table if exists dt_'+self.table_name+';');
                self.dstcur.execute('drop table if exists td_'+self.table_name+';');
                self.dstcur.execute('drop table if exists dic_'+self.table_name+';');
            
            self.dstcur.execute('create table abs_'+self.table_name+'(id int primary key, abs text);');
            self.dstcur.execute('create table dic_'+self.table_name+'(id int primary key, term text);');
            self.dstcur.execute('create table td_'+self.table_name+'(id int primary key, docs text);');
            self.dstcur.execute('create table dt_'+self.table_name+'(id int primary key, terms text);');
        elif 'tfidf' in param['pipeline']:
            self.src = sqlite3.connect(param['src']);
            self.srccur = self.src.cursor();
            self.table_name='dt_tfidf'+str(param['th']);
            if param['delete_tables']:
                self.srccur.execute('drop table if exists '+self.table_name+';');
            self.srccur.execute('create table '+self.table_name+'(id int primary key, terms text);');
          
    def __enter__(self):
      return self;
    
    def __exit__(self, type, value, traceback):
      self.src.close();
    
    def getRawROW(self):
        return self.srccur.fetchone()
    
    def getTD(self):
        self.srccur.execute('SELECT * FROM td_clean');
        return self.srccur.fetchall()
    
    def getDT(self):
        self.srccur.execute('SELECT * FROM dt_clean');
        return self.srccur.fetchall()
        
    def insertDoc(self,id,abs, terms):
        self.dstcur.execute('INSERT INTO abs_'+self.table_name+'(id, abs) VALUES (?, ?)', (id,abs));
        self.dstcur.execute('INSERT INTO dt_'+self.table_name+'(id, terms) VALUES (?, ?)', (id,str(terms)));
        for termID,num in terms.items():
            self.dstcur.execute("select docs from td_"+self.table_name+" where id=?", (termID,))
            docsOfTerm= self.dstcur.fetchone()
            if docsOfTerm is None: # new term
                rec =str({id:num})
                self.dstcur.execute('INSERT INTO td_'+self.table_name+'(id, docs) VALUES (?, ?)', (termID,rec));
            else:
                docsOfTerm=eval(docsOfTerm[0])
                docsOfTerm[id]=num
                rec=str(docsOfTerm)
                self.dstcur.execute("UPDATE td_"+self.table_name+" SET docs = ? WHERE id= ? """,(rec,termID))
        self.dst.commit();
    
    def insertDocs(self,IDs,Docs, DocTerms):
        for (id, abs, terms) in zip(IDs,Docs, DocTerms):
            self.dstcur.execute('INSERT INTO abs_'+self.table_name+'(id, abs) VALUES (?, ?)', (id,abs));
            self.dstcur.execute('INSERT INTO dt_'+self.table_name+'(id, terms) VALUES (?, ?)', (id,str(terms)));
            for termID,num in terms.items():
                self.dstcur.execute("select docs from td_"+self.table_name+" where id=?", (termID,))
                docsOfTerm= self.dstcur.fetchone()
                if docsOfTerm is None: # new term
                    rec =str({id:num})
                    self.dstcur.execute('INSERT INTO td_'+self.table_name+'(id, docs) VALUES (?, ?)', (termID,rec));
                else:
                    docsOfTerm=eval(docsOfTerm[0])
                    docsOfTerm[id]=num
                    rec=str(docsOfTerm)
                    self.dstcur.execute("UPDATE td_"+self.table_name+" SET docs = ? WHERE id= ? """,(rec,termID))
        self.dst.commit();
    
    
    def insert_tfidf(self,tfidf):
        n, i=len(tfidf), 0
        while i<n:  # this is more memory efficient for large lists
            self.srccur.execute('INSERT INTO '+self.table_name+'(id, terms) VALUES (?, ?)', (i,str(tfidf[i])));
            i+=1
        self.src.commit();
        
        
    def insertDic(self,dic):
        for i in range(len(dic)):
            self.dstcur.execute('INSERT INTO dic_'+self.table_name+'(id, term) VALUES (?, ?)', (i,dic[i]));
        self.dst.commit();
        
    def updateDic(self,dic):
        if not len(dic):
            return
        self.dstcur.execute("select count(*) from dic_"+self.table_name+";")
        n=self.dstcur.fetchone()[0]
        for (term,id) in dic.items():
            if id>=n:
                self.dstcur.execute('INSERT INTO dic_'+self.table_name+'(id, term) VALUES (?, ?)', (id,term));
        self.dst.commit();
        
    
    def log(self, str):
        with open(self.run_name+'.log','a') as fileout:
            print >> fileout , str
            fileout.flush()
           
        
