import sqlite3;

class dbConnector():
  def __init__(self, db_name):
    self.conn = sqlite3.connect(db_name);
    self.cur = self.conn.cursor();

  def __enter__(self):
    return self;

  def __exit__(self, type, value, traceback):
    self.conn.close();

  def saveInformation(self, values, table="test_parser"):
    for value in values:
      self.cur.execute('INSERT INTO '+table+'(raw_article, raw_front, journal_meta, \
        article_meta, kwd_group, raw_body, raw_back, ref_list) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (value[0], value[1], value[2], value[3], \
        value[4], value[5], value[6], value[7],));
    self.conn.commit();