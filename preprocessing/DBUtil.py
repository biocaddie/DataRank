import sqlite3;

class dbConnector():
  def __init__(self, db_name, dbver="raw"):
    self.dbver=dbver;
    self.src = sqlite3.connect(db_name);
    self.srccur = self.src.cursor();
    if dbver=="raw":
        self.srccur.execute('SELECT id,article_meta FROM test_parser');
    else:
        self.srccur.execute('SELECT id,abs FROM abs_raw');
    self.dst = sqlite3.connect('/'.join((db_name.split('/')[:-1]))+'/abstracts_clean.db');
    self.dstcur = self.dst.cursor();
    if dbver!="raw":
        self.dstcur.execute('drop table if exists abs_'+dbver+';');
        self.dstcur.execute('drop table if exists dt_'+dbver+';');
        self.dstcur.execute('drop table if exists td_'+dbver+';');
        self.dstcur.execute('drop table if exists dic_'+dbver+';');
    
    self.dstcur.execute('create table abs_'+dbver+'(id int primary key, abs text);');
    self.dstcur.execute('create table dic_'+dbver+'(id int primary key, term text);');
    self.dstcur.execute('create table td_'+dbver+'(id int primary key, docs text);');
    self.dstcur.execute('create table dt_'+dbver+'(id int primary key, terms text);');

  def __enter__(self):
    return self;

  def __exit__(self, type, value, traceback):
    self.src.close();

  def getROW(self):
      return self.srccur.fetchone()
  
      
  def insertDoc(self,docID,abs, terms):
    self.dstcur.execute('INSERT INTO abs_'+self.dbver+'(id, abs) VALUES (?, ?)', (docID,abs));
    self.dstcur.execute('INSERT INTO dt_'+self.dbver+'(id, terms) VALUES (?, ?)', (docID,str(terms)));
    for termID,num in terms.items():
        self.dstcur.execute("select docs from td_"+self.dbver+" where id=?", (termID,))
        docsOfTerm= self.dstcur.fetchone()
        if docsOfTerm is None: # new term
            rec =str({docID:num})
            self.dstcur.execute('INSERT INTO td_'+self.dbver+'(id, docs) VALUES (?, ?)', (termID,rec));
        else:
            docsOfTerm=eval(docsOfTerm[0])
            docsOfTerm[docID]=num
            rec=str(docsOfTerm)
            self.dstcur.execute("UPDATE td_"+self.dbver+" SET docs = ? WHERE id= ? """,(rec,termID))
    self.dst.commit();
    
  def insertDic(self,dic):
      for i in range(len(dic)):
          self.dstcur.execute('INSERT INTO dic_'+self.dbver+'(id, term) VALUES (?, ?)', (i,dic[i]));
      self.dst.commit();
