import re, sys, pprint, json

from collections import defaultdict

paper_author_temp = defaultdict(list)
author_paper_temp = defaultdict(list)
paper_journal_temp = {}
journal_paper_temp = defaultdict(list)
journal_count_temp = defaultdict(int)
author_count = defaultdict(int)


pattern_pid = re.compile('PMID- ')
pattern_author = re.compile('FAU - ')
pattern_journal = re.compile('JT  - ')

### CHANGE PARAMS
author_cutoff = 2
top_journals = 100

it = 0

# parse medline xml for:
#     paper -> journal
#     journal -> paper
#     journal count
#     paper -> authors
#     authors -> paper
#     author count
for batch in xrange(1,16):
    f = open('/home/hchen/biocaddie/scripts/out/medline/TEN_sunday/Medline_batch'+str(batch)+'.xml','r')
    raw_text = f.read()
    f.close()
    articleList = re.split('\n{2,}', raw_text)

    for article in articleList:
        it += 1
        if it % 1000 == 0:
            print 'parsed paper', it
        pmid = re.findall('PMID- .*', article)[0][6:]
        paper_author_temp[pmid] = []
        journal = re.findall('JT  - .*', article)[0][6:]
        paper_journal_temp[pmid] = journal
        journal_paper_temp[journal].append(pmid)
        journal_count_temp[journal] += 1
        fau_matches = re.findall('FAU - .*', article)
        if len(fau_matches) > 0:
            if len(fau_matches) >= 4:
                matches = fau_matches[:3] + [fau_matches[-1]]
            else:
                matches = fau_matches
            for a in matches:
                author_count[a[6:]] += 1
                author_paper_temp[a[6:]].append(pmid)
                paper_author_temp[pmid].append(a[6:])
        else:
            del paper_author_temp[pmid]
            del paper_journal_temp[pmid]


print '\nunprocessed author count', len(author_count)
print 'unprocessed paper count', len(paper_journal_temp)
print 'unprocessed journal count', len(journal_paper_temp), '\n'


# author_list = author_count.keys()
# paper_list = list(set([item for sublist in author_paper_temp.values() for item in sublist]))


#### ADDITIONAL DATA CLEANING TO FILTER JOURNALS
journal_count = {}
top_100_journals = sorted(journal_count_temp, key=journal_count_temp.get, reverse=True)[:top_journals]
for j in top_100_journals:
    journal_count[j] = journal_count_temp[j]


# delete authors with less than 2 papers
trunc_author_count = {}
deleted = 0
for k,v in author_count.items():
    if v > author_cutoff:
        trunc_author_count[k] = v
    else:
        deleted += 1
print 'deleted', deleted, 'authors with less than 2 papers\n'

author_paper = {}
paper_author = {}
paper_journal = {}
journal_paper = {}

author_list = trunc_author_count.keys()
for a in author_list:
    # remove papers not in top 100 journals from author_paper lookup
    author_paper[a] = [x for x in author_paper_temp[a] if paper_journal_temp[x] in journal_count]
print '\tdone with author_paper'

for k,v in author_paper.items():
    author_paper[k] = list(set(v))


paper_list = list(set([item for sublist in author_paper.values() for item in sublist]))
for p in paper_list:
    # remove authors with less than 2 papers from paper_author lookup
    paper_author[p] = [a for a in paper_author_temp[p] if a in author_list]
    paper_journal[p] = paper_journal_temp[p]
print '\tdone with paper_author'
print '\tdone with paper_journal'


for j in top_100_journals:
    # remove papers not written by authors with more than 2 papers from journal_paper lookup 
    journal_paper[j] = [p for p in journal_paper_temp[j] if p in paper_author]
print '\tdone with journal_paper'

print '\nfinal author count:', len(trunc_author_count), '(check:', len(trunc_author_count)==len(author_paper), ')'
print 'document count:', len(paper_list), '(check:', len(paper_list)==len(paper_journal),')\n'







# #############UNCOMMENT FOR CORANK
# fout = open('out/corank_author_paper.json','w')
# fout.write(json.dumps(author_paper_temp))
# print 'dumped author_paper to json...'

# fout = open('out/corank_paper_author.json', 'w')
# fout.write(json.dumps(paper_author_temp))
# print 'dumped paper_author to json...'

# fout = open('out/corank_author_list.json', 'w')
# fout.write(json.dumps(author_list))
# fout = open('out/corank_paper_list.json', 'w')
# fout.write(json.dumps(paper_list))

#############UNCOMMENT FOR MULTIRANK

fout = open('out/FINAL_author_paper.json','w')
fout.write(json.dumps(author_paper))
print 'dumped author_paper to json...'

fout = open('out/FINAL_paper_author.json', 'w')
fout.write(json.dumps(paper_author))
print 'dumped paper_author to json...'

fout = open('out/FINAL_paper_journal.json', 'w')
fout.write(json.dumps(paper_journal))
print 'dumped paper_journal to json...'

fout = open('out/FINAL_journal_paper.json', 'w')
fout.write(json.dumps(journal_paper))
print 'dumped journal_paper to json...'


fout = open('out/FINAL_author_list.json', 'w')
fout.write(json.dumps(author_list))
fout = open('out/FINAL_paper_list.json', 'w')
fout.write(json.dumps(paper_list))
fout = open('out/FINAL_journal_list.json', 'w')
fout.write(json.dumps(top_100_journals))
print 'dumped lists...\n'

fout.close()

