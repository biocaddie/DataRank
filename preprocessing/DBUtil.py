import sqlite3;

class dbConnector():
  def __init__(self, param):
    self.table_name=param['table_name'];
    self.src = sqlite3.connect(param['src']);
    self.srccur = self.src.cursor();
    self.srccur.execute('SELECT id,article_meta FROM test_parser');
    self.dst = sqlite3.connect(param['dst']);
    self.dstcur = self.dst.cursor();
    if self.table_name!="raw":
        self.dstcur.execute('drop table if exists abs_'+self.table_name+';');
        self.dstcur.execute('drop table if exists dt_'+self.table_name+';');
        self.dstcur.execute('drop table if exists td_'+self.table_name+';');
        self.dstcur.execute('drop table if exists dic_'+self.table_name+';');
    
    self.dstcur.execute('create table abs_'+self.table_name+'(id int primary key, abs text);');
    self.dstcur.execute('create table dic_'+self.table_name+'(id int primary key, term text);');
    self.dstcur.execute('create table td_'+self.table_name+'(id int primary key, docs text);');
    self.dstcur.execute('create table dt_'+self.table_name+'(id int primary key, terms text);');

  def __enter__(self):
    return self;

  def __exit__(self, type, value, traceback):
    self.src.close();

  def getROW(self):
      return self.srccur.fetchone()
  
      
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
    
  def insertDic(self,dic):
      for i in range(len(dic)):
          self.dstcur.execute('INSERT INTO dic_'+self.table_name+'(id, term) VALUES (?, ?)', (i,dic[i]));
      self.dst.commit();
