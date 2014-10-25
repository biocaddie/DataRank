#!/usr/bin/env python
import sys;
from extrModule import ExtractionFactory as extr;
from dbModule import DBFactory as lite;
from dbList import patterns;

def Main(argv):
  tags = patterns;
  source = extr.getSource(argv[1]);
  with extr.ResultFile(argv[2]) as file:
    result_array = {item:0 for item in tags};
    (size, result_array) = extr.extrDBItems(result_array, source); 
    result_array['size'] = size;
    file.saveResult(result_array);
  pass;

# Argv_1: Source File
# Argv_2: Result List
if __name__ == '__main__':
  Main(sys.argv);   