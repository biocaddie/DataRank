import sqlite3;

class dbConnector():
  def __init__(self, param):
    if 'clean' in param['pipeline'] or 'parse' in param['pipeline']:
        self.prev_dic_size=0
        self.run_name=param['run_name'];
        self.table_name=param['table_name'];
        self.src = sqlite3.connect(param['src']);
        self.srccur = self.src.cursor();
        self.srccur.execute('SELECT id,article_meta FROM test_parser');
        self.dst = sqlite3.connect(param['dst']);
        self.dstcur = self.dst.cursor();
        if self.delete_tables:
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
        self.srccur.execute('drop table if exists dt_tfidf;');
        self.srccur.execute('create table dt_tfidf(id int primary key, terms text);');
        
        
        

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
      
  def insertDoc(self,docID,abs, terms):
    self.dstcur.execute('INSERT INTO abs_'+self.table_name+'(id, abs) VALUES (?, ?)', (docID,abs));
    self.dstcur.execute('INSERT INTO dt_'+self.table_name+'(id, terms) VALUES (?, ?)', (docID,str(terms)));
    for termID,num in terms.items():
        self.dstcur.execute("select docs from td_"+self.table_name+" where id=?", (termID,))
        docsOfTerm= self.dstcur.fetchone()
        if docsOfTerm is None: # new term
            rec =str({docID:num})
            self.dstcur.execute('INSERT INTO td_'+self.table_name+'(id, docs) VALUES (?, ?)', (termID,rec));
        else:
            docsOfTerm=eval(docsOfTerm[0])
            docsOfTerm[docID]=num
            rec=str(docsOfTerm)
            self.dstcur.execute("UPDATE td_"+self.table_name+" SET docs = ? WHERE id= ? """,(rec,termID))
    self.dst.commit();
    
  def insert_tfidf(self,tfidf):
      n, i=len(tfidf), 0
      while i<0:  # this is more memory efficient for large lists
          self.srccur.execute('INSERT INTO dt_tfidf(id, term) VALUES (?, ?)', (i,str(tfidf[i])));
          i+=1
      
      
  def insertDic(self,dic):
      for i in range(len(dic)):
          self.dstcur.execute('INSERT INTO dic_'+self.table_name+'(id, term) VALUES (?, ?)', (i,dic[i]));
      self.dst.commit();
      
  def updateDic(self,dic):
      for i in range(self.prev_dic_size,len(dic)):
          self.dstcur.execute('INSERT INTO dic_'+self.table_name+'(id, term) VALUES (?, ?)', (i,dic[i]));
      self.dst.commit();
  
  def log(self, str):
    with open(self.run_name+'.log','a') as fileout:
        print >> fileout , str
        fileout.flush()
         
      
