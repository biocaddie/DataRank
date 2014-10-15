#!/usr/bin/env python
import sys;
from extrModule import ExtractionFactory as extr;

def Main(argv):
  tag_file = argv[1];
  source_file = argv[2];

  tags = extr.getTags(tag_file);
  source = extr.getSource(source_file);

  testTag = tags[0];
  extr.extrFeatures(testTag, source);
  pass;

# Argv_1: Pattern File Name
# Argv_2: Source File Name
if __name__ == '__main__':
  Main(sys.argv);