import re;

# Return Tags Array
def getTags(name_file):
  return open(name_file, 'r').read().split('\n');

# Return Source File as String
def getSource(name_file):
  return open(name_file, 'r').read();

# Return ALL Matched Content as Array of String
def extrFeatures(tag, source):
  DEFAULT_VALUE = ['0'];
  if not source or source == DEFAULT_VALUE:
    return DEFAULT_VALUE;
  pattern = '<'+tag+'[^>]*?>'+'(.*?)'+'</'+tag+'>';
  matched_patterns = re.findall(pattern, source, re.DOTALL);
  return matched_patterns if matched_patterns else DEFAULT_VALUE;

# Extractor for one group of features for one article.
DEFAULT_SONS = "default_sons";
class FeatureExtractor():
  def __init__(self, tag_string):
    self.father, self.sons = re.search('(.*?)\((.*?)\)', tag_string).group(1, 2);
    self.sons = re.sub(' ', '', self.sons);
    self.sons = self.sons.split(",") if self.sons else DEFAULT_SONS;

  def extrFeatures(self, source):
    content = extrFeatures(self.father, source)[0];
    features = [content];
    if self.sons != DEFAULT_SONS:
      features += [extrFeatures(son, content)[0] for son in self.sons];
    return features;
      
# Extractor for All Articles
DEFAULT_TAGS = "front(journal-meta, article-meta, kwd-group)\nbody()\nback(ref-list)"
class BatchParser():
  def __init__(self, tag_text = DEFAULT_TAGS, unit_name = "article"):
    self.unit_name = unit_name;
    self.tags = tag_text;

  def parseBatch(self, source):
    extractors = [FeatureExtractor(tag_string) for tag_string in self.tags];
    result_array = [];
    for content in extrFeatures(self.unit_name, source):
      temporary_array = [content];
      for extractor in extractors:
        temporary_array += extractor.extrFeatures(content);
      result_array.append(temporary_array);
    return result_array;