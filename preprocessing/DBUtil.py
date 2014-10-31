import sqlite3;

class dbConnector():
  def __init__(self, db_name):
    self.src = sqlite3.connect(db_name);
    self.srccur = self.src.cursor();
    self.srccur.execute('SELECT id,article_meta FROM test_parser');
    self.dst = sqlite3.connect('/'.join((db_name.split('/')[:-1]))+'/abstracts.db');
    self.dstcur = self.dst.cursor();
    self.dstcur.execute('drop table if exists abs_raw;');
    self.dstcur.execute('drop table if exists dt_raw;');
    self.dstcur.execute('drop table if exists td_raw;');
    self.dstcur.execute('drop table if exists dic_raw;');
    
    self.dstcur.execute("create table abs_raw(id int primary key, abs text);");
    self.dstcur.execute('create table dic_raw(id int primary key, term text);');
    self.dstcur.execute('create table td_raw(id int primary key, docs text);');
    self.dstcur.execute('create table dt_raw(id int primary key, terms text);');

  def __enter__(self):
    return self;

  def __exit__(self, type, value, traceback):
    self.src.close();

  def getROW(self):
      return self.srccur.fetchone()
  
      
  def insertDoc(self,docID,abs, terms, table="raw"):
    self.dstcur.execute('INSERT INTO abs_'+table+'(id, abs) VALUES (?, ?)', (docID,abs));
    self.dstcur.execute('INSERT INTO dt_'+table+'(id, terms) VALUES (?, ?)', (docID,str(terms)));
    for termID,num in terms.items():
        self.dstcur.execute("select docs from td_"+table+" where id=?", (termID,))
        docsOfTerm= self.dstcur.fetchone()
        if docsOfTerm is None: # new term
            rec =str({docID:num})
            self.dstcur.execute('INSERT INTO td_'+table+'(id, docs) VALUES (?, ?)', (termID,rec));
        else:
            docsOfTerm=eval(docsOfTerm[0])
            docsOfTerm[docID]=num
            rec=str(docsOfTerm)
            self.dstcur.execute("UPDATE td_"+table+" SET docs = ? WHERE id= ? """,(rec,termID))
    self.dst.commit();
    
  def insertDic(self,dic, table="raw"):
      for i in range(len(dic)):
          self.dstcur.execute('INSERT INTO dic_'+table+'(id, term) VALUES (?, ?)', (i,dic[i]));
      self.dst.commit();
