#!/usr/bin/env python
import sys;
from extrModule import ExtractionFactory as extr;

def Main(argv):
  tag_file = argv[1];
  source_file = argv[2];

  tags = extr.getTags(tag_file);
  source = extr.getSource(source_file);

  print tags;
  # test_tag = tags[3];
  for test_tag in tags:
    print(test_tag);
    # print extr.extrFeatures('frot', source);
    article_extractor = extr.FeatureExtractor(test_tag);
    result = article_extractor.extrFeatures(source);
    print("\n".join([item for item in result]));

  # test_tag = tags[0];
  # article_extractor = extr.FeatureExtractor(test_tag);
  # result = article_extractor.extrFeatures(source);
  # print("\n".join([item for item in result]));

  pass;

# Argv_1: Pattern File Name
# Argv_2: Source File Name
if __name__ == '__main__':
  Main(sys.argv);