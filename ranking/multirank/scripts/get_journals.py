import re, sys, pprint, json
# from optparse import OptionParser
from collections import defaultdict

paper_journals = {}

it = 0
for batch in xrange(1,7):
    f = open('/home/hchen/biocaddie/scripts/out/medline/Medline_batch'+str(batch)+'.xml','r')
    raw_text = f.read()
    f.close()
    articleList = re.split('\n{2,}', raw_text)

    for article in articleList:
        it += 1
        if it % 1000 == 0:
            print 'parsed paper', it
        pmid = re.findall('PMID- .*', article)[0][6:]
        journal = re.findall('JT  - .*', article)[0][6:]
        paper_journals[pmid] = journal


fout = open('out/breast_cancer_paper_journal_deg2.json','w')
fout.write(json.dumps(paper_journals))
print 'dumped parsed MEDLINE dictionary to json...'


journal_list = defaultdict(int)
for k,v in paper_journals.items():
    journal_list[v] += 1

fout = open('out/breast_cancer_paper_journal_count_deg2.json','w')
fout.write(json.dumps(journal_list))
print 'dumped parsed journal list to json...', len(journal_list)

fout.close()

top_100_journals = sorted(journal_list, key=journal_list.get, reverse=True)[:100]
top_paper_journals = {}

for k,v in paper_journals.items():
    if v in top_100_journals:
        top_paper_journals[k] = v

fout = open('out/breast_cancer_paper_journal_TOP100_deg2.json','w')
fout.write(json.dumps(top_paper_journals))
print 'dumped papers for TOP 100 journals to json...', len(top_paper_journals)

fout.close()