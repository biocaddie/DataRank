from collections import defaultdict
import sqlite3;

class dbConnectorMesh():
  def __init__(self, db_name):
    self.conn = sqlite3.connect(db_name);
    self.cur = self.conn.cursor();
    self.row_factory = lambda cursor, row: row[0]


  def __enter__(self):
    return self;

  def __exit__(self, type, value, traceback):
    self.conn.close();

  def saveInformation(self, dictionary, table):
    for pmid,header in dictionary.iteritems():
      self.cur.execute('INSERT INTO '+table+'(pmid, header) \
      VALUES (?, ?);', (pmid, str(header)))
    self.conn.commit();

  def makeMeshEntry(self, dictionary, table):
    for header,entries in dictionary.iteritems():
      self.cur.execute('INSERT INTO '+table+'(header, entry_terms) \
      VALUES (?, ?);', (str(header), str(entries)))
      # print str(header)
    self.conn.commit();

  def makeArticleEntry(self, dictionary, table):
    for pmid,mesh in dictionary.iteritems():
      try:
        self.cur.execute('INSERT INTO '+table+'(pmid, header) \
        VALUES (?, ?);', (int(pmid), str(mesh)))
      except sqlite3.IntegrityError:
        print "double pmid", str(pmid)
      # print str(header)
    self.conn.commit();


# CREATE TABLE article_mesh
# (
# pmid INTEGER PRIMARY KEY,
# header TEXT
# );

# CREATE TABLE header_entry
# (
# header TEXT PRIMARY KEY,
# entry_terms TEXT
# );

# CREATE TABLE mesh_entry
# (
# header TEXT PRIMARY KEY,
# entry_terms TEXT
# );
