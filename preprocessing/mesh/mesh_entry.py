#!/usr/bin/env python
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
parser.add_option('-d', '--database', dest='db', default='medline.db',
                help="database for sqlite3 connect")
parser.add_option('-t', '--table1', dest='table1', default='mesh_entry',
                help="table name to map mesh header with entry terms")
(options, args) = parser.parse_args()

mesh_entry = {}
mesh_headers = []

pattern_header = re.compile('MH = ')
pattern_entry = re.compile('ENTRY = ')

f = open(options.source,'r')
raw_text = f.read()
articleList = re.split('\n{2,}', raw_text)

for article in articleList:
	lines = article.split('\n')
	for line in lines:
		if pattern_header.match(line):
			header = line[5:]
			mesh_headers.append(header)
			mesh_entry[header] = []
	for line in lines:
		if pattern_entry.match(line):
			entries = line[8:].split('|')
			mesh_entry[header].append(entries)

f.close()

for key in mesh_entry:
	temp = [item for sublist in mesh_entry[key] for item in sublist]
	mesh_entry[key] = list(set(temp))

# print len(mesh_entry.keys())
# b = mesh_entry.keys()
# print len(b)
# a = set(mesh_entry.keys())
# print len(a)
# entries = [entry for inner in mesh_entry.values() for entry in inner]
# sanity = defaultdict(int)
# for x in entries:
# 	sanity[x] += 1
# print len(sanity.keys())

with lite.dbConnectorMesh(options.db) as db_conn:
    db_conn.makeMeshEntry(mesh_entry, options.table1);
pass;