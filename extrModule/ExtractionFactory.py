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

