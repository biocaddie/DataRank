#!/usr/bin/env python
import sys;
from extrModule import ExtractionFactory as extr;
from dbModule import DBFactory as lite;

def Main(argv):
  tags = extr.getTags(argv[1]);
  source = extr.getSource(argv[2]);

  parser = extr.BatchParser(tags);
  data = parser.parseBatch(source);
  with lite.dbConnector(argv[3]) as db_conn:
    db_conn.saveInformation(data);
  pass;

# Argv_1: Pattern File Name
# Argv_2: Source File Name
# Argv_3: Database Name
if __name__ == '__main__':
  Main(sys.argv);