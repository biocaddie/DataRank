import sys, os, json, pdb, itertools
import pprint as pp
import datetime as dt
from collections import defaultdict
from operator import itemgetter

# load parsed MEDLINE data
author_paper = json.load(open('out/FINAL_author_paper.json','r'))
paper_author = json.load(open('out/FINAL_paper_author.json', 'r'))
paper_journal = json.load(open('out/FINAL_paper_journal.json', 'r'))
journal_paper = json.load(open('out/FINAL_journal_paper.json', 'r'))

# author_list = json.load(open('out/FINAL_author_list.json', 'r'))
# paper_list_original = json.load(open('out/FINAL_paper_list.json', 'r'))
journal_list = json.load(open('out/FINAL_journal_list.json', 'r'))

source_cited = json.load(open('out/medline/breast_cancer_cited_by_TEN_sunday.json', 'r'))

paper_to_dataset_temp = defaultdict(list)
source_paper_to_dataset = json.load(open('out/medline/breast_cancer_paper_to_dataset_TEN_sunday.json', 'r'))
for k in source_paper_to_dataset:
    paper_to_dataset_temp[k] = source_paper_to_dataset[k]



b_cancer = {'GSE1378': '15193263', 'GSE1456':'16280042', 'GSE2034':'15721472', 'GSE2607':'16626501', 'GSE2990':'16478745', 'GSE3143': '16273092', 'GSE3281':'12297621', 'GSE3453':'16505412', 'GSE3494':'16141321', 'GSE4006': '16809442', 'GSE4025':'16849584'}
originals = [v for v in b_cancer.values() if v in paper_journal]
# datasets = [k for k,v in b_cancer.items() if v in paper_journal]

# citation network for documents with top 100 journals
cited_by = {}
for k,v in source_cited.items():
    if k in paper_journal:
        cited_by[k] = [x for x in v if x in paper_journal]

for k,v in cited_by.items():
    dataset = paper_to_dataset_temp[k]
    for p in v:
        paper_to_dataset_temp[p].extend(dataset)

for k,v in paper_to_dataset_temp.items():
    paper_to_dataset_temp[k] = list(set(v))

paper_to_dataset = {}
for p in paper_journal:
    paper_to_dataset[p] = paper_to_dataset_temp[p]


# blah = list(itertools.chain.from_iterable(cited_by.values()))
# blah2 = blah + cited_by.keys()
# blah2 = list(set(blah2))


# invert cited_by mapping to get cites, filters paper for journals
cites = defaultdict(list)
for k, v in cited_by.iteritems():
    for pmid in v:
        if pmid in paper_journal:
            cites[pmid].append(k)
        if pmid not in paper_to_dataset:
            print pmid

merged = list(itertools.chain.from_iterable(cites.values()))
paper_list_trunc = merged + cites.keys()
paper_list_trunc = list(set(paper_list_trunc))




author_list = []
for p in paper_list_trunc:
    author_list.extend(paper_author[p])
author_list = list(set(author_list))
paper_list = paper_list_trunc

##### NEEDED FOR CORANK
## key is author, for each author there is dict of counts of coauthor (for edge weights)
coauthors = defaultdict(lambda : defaultdict(int))
for paper, authors in paper_author.items():
    if paper in paper_list:
        authors = [a for a in authors if a in author_list]
        # make coauthor dictionary
        auth_perm = list(itertools.permutations(authors,2))
        for pair in auth_perm:
            coauthors[pair[0]][pair[1]] += 1


### basic statistics
print 'statistics:'
print '\t num authors:', len(author_list)
print '\t num documents in citation network:', len(paper_list_trunc)
print '\t num journals (category concepts):', len(journal_list), '\n'

print 'dictionaries available for lookup: \n \t paper_author, author_paper, paper_journal, paper_to_dataset \n'
print 'lists for reference: \n \t author_list, paper_list, journal_list \n'