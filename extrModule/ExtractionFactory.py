import re;

# Return Tags Array
def getTags(name_file):
  return open(name_file, 'r').read().split('\n');

# Return Source File as String
def getSource(name_file):
  return open(name_file, 'r').read();

# Return ALL Matched Content as Array of String
def extrFeatures(tag, source):
  pattern = '<'+tag+'[^>]*?>'+'(.*?)'+'</'+tag+'>';
  matched_patterns = re.findall(pattern, source, re.DOTALL);
  return matched_patterns;

# Extractor, not Supporting Resursive Extraction, Must be Unique Tag.
DEFAULT_SONS = "default_sons";
class FeatureExtractor():
  def __init__(self, tag_string, further_extraction = False):
    self.father, self.sons = re.search('(.*?)\((.*?)\)', tag_string).group(1, 2);
    self.sons = re.sub(' ', '', self.sons);
    self.sons = self.sons.split(",") if self.sons else DEFAULT_SONS;

  def extrFeatures(self, source):
    results = [];
    for content in extrFeatures(self.father, source):
      features = [content];
      if self.sons != DEFAULT_SONS:
        features += [extrFeatures(son, content)[0] for son in self.sons];
      results.append(features);
    return results;
      




