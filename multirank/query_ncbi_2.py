#!/usr/local/bin/python
import os, pdb
import datetime as dt
import json
from Bio import Entrez, Medline
from collections import defaultdict


deg = 2



def chunks(l, n):
    """ Yield successive n-sized chunks from input list """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_Medline(pubmed_ids, batch):
    query = ",".join(pubmed_ids)
    handle = Entrez.efetch(db="pubmed", id=query, rettype="medline", retmode="text")
    record = handle.read()
    handle.close()
    fout = open('out/medline/TEN/Medline_batch'+str(batch)+'.xml', 'a')
    fout.write(record)

def get_cited_by(pmid):
    """ input: pmid
        output: pmc_id list that input is cited by """
    get_pmc = Entrez.elink(dbfrom="pubmed", db="pmc", LinkName="pubmed_pmc_refs", from_uid=pmid)
    search_results = Entrez.read(get_pmc)
    if len(search_results[0]['LinkSetDb']) > 0:
        pmc_ids = [link["Id"] for link in search_results[0]["LinkSetDb"][0]["Link"]]
        print 'number of references for', pmid, ':', len(pmc_ids)
    else:
        pmc_ids = []
        print 'ncbi query empty return for paper', pmid
    return pmc_ids

def convert_pmc_to_pmid(pmc_ids):
    """ input: list of pmc_ids
        output: corresponding list of pmids """
    # split pmc_id list for smaller batch queries
    pubmed_ids = []
    pmc_chunks = chunks(pmc_ids, 50)
    for chunk in pmc_chunks:
        temp_results = Entrez.read(Entrez.elink(dbfrom="pmc", db="pubmed", LinkName="pmc_pubmed",from_uid=",".join(chunk)))
        if len(temp_results[0]['LinkSetDb']) > 0:
            pubmed_ids.extend([link["Id"] for link in temp_results[0]["LinkSetDb"][0]["Link"]])
    return list(set(pubmed_ids))

Entrez.email="hechen@ucsd.edu"

b_cancer = {'GSE1378': ['15193263'], 'GSE1456':['16280042'], 'GSE2034':['15721472'], 'GSE2607':['16626501'], 'GSE2990':['16478745'], 'GSE3143': ['16273092'], 'GSE3281':['12297621'], 'GSE3453':['16505412'], 'GSE3494':['16141321'], 'GSE4006': ['16809442'], 'GSE4025':['16849584']}

cited_by = {}
paper_list = [item for sublist in b_cancer.values() for item in sublist]

start = dt.datetime.now()
batch = 0
for series, original in b_cancer.items():
    batch += 1
    get_Medline(original, batch)
    pmc_ids = get_cited_by(original)
    pmids = convert_pmc_to_pmid(pmc_ids)
    cited_by[original[0]] = pmids
    get_Medline(pmids, batch)
    paper_list.extend(pmids)
    b_cancer[series].extend(pmids)
    # print len(paper_list)
end = dt.datetime.now()
time_diff = divmod((end - start).total_seconds(), 60)
print 'elapsed time:', time_diff[1], 'sec ...'
print 'number of cited papers', len(cited_by)
print 'paper corpus size', len(paper_list)


paper_to_dataset = defaultdict(list)
for k, v in b_cancer.iteritems():
    for pmid in v:
        paper_to_dataset[pmid].append(k)


it = 0
for x in range(deg-1):
    to_add = []
    start = dt.datetime.now()
    for paper in paper_list:
        if it % 1000 == 0:
            batch += 1
        it += 1
        if paper not in cited_by:
            pmc_ids = get_cited_by(paper)
            if len(pmc_ids) > 0:
                pmids = convert_pmc_to_pmid(pmc_ids)
                if len(pmids) > 0:
                    cited_by[paper] = pmids
                    get_Medline(pmids, batch)
                    to_add.extend(pmids)
    paper_list.extend(to_add)
    paper_list = list(set(paper_list))
    end = dt.datetime.now()
    time_diff = divmod((end - start).total_seconds(), 60)
    print 'elapsed time (deg '+str(x+2)+':', time_diff[1], 'sec ...'
    print 'added', len(to_add), 'new papers (may have double count)'
    print 'new paper corpus size', len(paper_list)



fout = open('out/medline/breast_cancer_paper_to_dataset.json','w')
fout.write(json.dumps(paper_to_dataset))
print 'dumped paper_to_dataset dictionary to json...'

fout = open('out/medline/breast_cancer_cited_by.json','w')
fout.write(json.dumps(cited_by))
print 'dumped dictionary to json...'


paper_list = list(set(paper_list))
fout = open('out/medline/breast_cancer_papers.json','w')
fout.write(json.dumps(paper_list))
print 'dumped document list to json...'

fout.close()