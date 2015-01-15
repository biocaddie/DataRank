import re
import sys
from optparse import OptionParser
from collections import defaultdict
import DBFactoryMesh as lite;
from collections import Counter
import pprint
from itertools import chain

usage = "usage: prog [options] arg1 arg2"
parser = OptionParser(usage=usage)
parser.add_option('-s', '--source', dest='source',
              	help="source txt file to get mesh terms")
parser.add_option('-d', '--database', dest='db', default='mesh.db',
                help="database for sqlite3 connect")
parser.add_option('-t', '--table1', dest='table1', default='article_mesh',
                help="table name to map mesh header with entry terms")
(options, args) = parser.parse_args()

article_mesh = {}

pattern_pid = re.compile('PMID- ')
pattern_mesh = re.compile('MH  - ')

f = open(options.source,'r')
raw_text = f.read()
articleList = re.split('\n{2,}', raw_text)

for article in articleList:
	lines = article.split('\n')
	for line in lines:
		if pattern_pid.match(line):
			pmid = line[6:]
			article_mesh[pmid] = []
	for line in lines:
		if pattern_mesh.match(line):
			mesh = line[6:]
			article_mesh[pmid].append(mesh)

f.close()

print len(article_mesh.keys())

with lite.dbConnectorMesh(options.db) as db_conn:
    db_conn.makeArticleEntry(article_mesh, options.table1);
pass;

