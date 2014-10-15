#!/usr/bin/env python
import sys
from extrModule import ExtractionFactory as extr

def main(argv):
  extr.extrFeatures("ii","iii");
  pass;

if __name__ == '__main__':
  main(sys.argv);