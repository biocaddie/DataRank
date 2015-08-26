import ast, itertools, sys, time, math
from search.models import Dataset
import pandas as pd
import numpy as np
from sklearn.externals import joblib
sys.stderr = open('/home/arya/datarank.log','w')
def saveOne(row):
    d = Dataset()
    d.ID = row.accession
    d.Url = "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + row.accession
    d.PMID= row.pmid
    d.Summary= row.summary
    d.Title= row.accession+': '+row.title
    d.Features = ';'.join(row.mesh)
    d.Count = row.cpcc
    d.save()
 
def saveAll():
    d=pd.read_pickle('/home/arya/PubMed/GEO/Datasets/D.Web.df')
    d.apply(saveOne,axis=1)
 
 
 
datasets = Dataset.objects.all()
dsID=map(lambda x: x.ID,datasets)
if not len(datasets):
    print >>sys.stderr, "Saving Datasets to Django Database... "
    saveAll()
    datasets = Dataset.objects.all()
print >>sys.stderr, "Read #Datasets: "+str(len(datasets))

print >>sys.stderr, "Reading SVM Model... "
M=pd.read_pickle('/home/arya/PubMed/GEO/Datasets/M.df')
M.index=map(str.lower,M.name.values)
model=joblib.load('/home/arya/PubMed/GEO/Datasets/libsvm/model/Model.libsvm')
DP=pd.read_pickle('/home/arya/PubMed/GEO/Datasets/DPP.df')[['accession','cited_pmid']].drop_duplicates()
PMID=pd.DataFrame(data=model.classes_.astype(int).astype(str), columns=['cited_pmid'])
PMID['deci_idx']=PMID.index
DP['deci']=0
DP=pd.merge(DP,PMID,on='cited_pmid')
print >>sys.stderr, "Reading Done. "
# deci=np.random.rand(DP.cited_pmid.unique().shape[0])






RANKING_SIZE = 5000
# general algorithm is used to reduce #samples
def normList(alist_raw, func=lambda x: x, func2=lambda x: x):
    alist = [func2(a) for a in alist_raw]
    SUM = 1.*sum(alist)
    try:
        return [func(a/SUM) for a in alist]
    except :
        return [0. for a in alist]
def normOnLog(alist, func = lambda x: x):
    m = max(alist)
    return [func(a-m) for a in alist]

getJaccard = lambda x, y: 1.*len(x.intersection(y))/len(x.union(y))
getLog = lambda x: math.log(1e-200+x)
getExp = lambda x: math.exp(x)
def getSimilarity(dataset1, dataset2):
    dataset1 = dataset1.lower().strip(';')
    dataset2 = dataset2.lower().strip(';')

    if len(dataset1) == 0:
        raise ValueError
    x_raw = dataset1.split(';')
    x_r2 = [d.strip() for d in x_raw]
    x = set(x_r2)

    y_raw = dataset2.split(';')
    y_r2 = [d.strip() for d in y_raw]
    y = set(y_r2)
    return getJaccard(x, y)

def normMultiply(jaccs, counts, datasets):
    pd.DataFrame(counts).to_pickle('/home/arya/c.df')
    pd.DataFrame(jaccs).to_pickle('/home/arya/j.df')
    n_jaccs = normList(jaccs, func=getLog)
    n_counts = normList(counts, func=getLog)
    results = [j+c for j, c in zip(*[n_jaccs, n_counts])]
    n_results_temp = normOnLog(results, func=getExp)
    n_results = normList(n_results_temp, getLog)
    lists = zip(*[n_results, datasets, n_jaccs, jaccs])
    return lists

def jaccardRelevance(keywords,datasets):
    print >>sys.stderr, "Ranking via Jaccard. keywords: "+str(keywords)
    return [getSimilarity(keywords, st.Features) for st in datasets]

    
 
def SVMRelevance(keywords, datasets):
    print >>sys.stderr, "Ranking via SVM. keywords: "+str(keywords)
    from scipy.sparse import csr_matrix
    x= csr_matrix((1,27454))
    for w in keywords.split(';'):
        try:
            x[0,int(M.loc[w.strip().lower()].mid)-1]+=1
        except:
            pass
    print >>sys.stderr,'Feature Vector Data:' , x.data, 'idx:',x.nonzero()[1]
    deci=model.decision_function(x)[0]
    DP.index=DP.cited_pmid
    DP.deci.loc[PMID.cited_pmid]=deci[DP.loc[PMID.cited_pmid].deci_idx.values]
    DP.index=DP.accession
    MIN=min(DP.loc[dsID].deci.values)
    if MIN <0:
        return DP.loc[dsID].deci.values-MIN
    else: 
        return DP.loc[dsID].deci.values

def generalRanking(keywords):
    try:
#         relevance = jaccardRelevance(keywords,datasets)
        relevance = SVMRelevance(keywords,datasets)
        importance = [np.log(st.Count+1)/10.0 for st in datasets]
        lists = normMultiply(relevance, importance, datasets)
    except ValueError:
        return None
    sort = sorted(lists, key=lambda x: (x[0], x[1].ID), reverse=True)
    return sort

# use passed datasets to re-rank
def getRating(datatuple, ratings):
    rate , dataset, log_filling, filling = datatuple
    try:
        return (int(ratings[dataset.ID]), dataset, rate, log_filling, filling)
    except KeyError:
        return (0, dataset, rate, log_filling, filling)

def fillRatings(dataset, sample_argument):
    samples, sample_rates = sample_argument
#     size = len(sample_rates)*1.
    try:
        ind = samples.index(dataset)
        rate = sample_rates[ind]
        sum_dist = 1
    except ValueError:
        dists = [getSimilarity(dataset.Features, sample.Features) for sample in samples]
        rate = sum([d*r for d,r in zip(dists, sample_rates)])
        sum_dist = 1. * sum(dists)
    try:
        result = rate / sum_dist
    except ZeroDivisionError:
        result = 1e-200
    return result

def preferenceRanking(offline_log_value, all_datasets, raw_user_ratings):
    exponentialized_offline_value = [getExp(r) for r in offline_log_value]
    raw_user_ratings = ast.literal_eval(raw_user_ratings)
    
    start = time.time()
    samples, sample_rates = zip(*[(Dataset.objects.get(ID=key), float(value)) for key,value in raw_user_ratings.iteritems() if value != '0'])
    print >> sys.stderr, len(samples)
    print >> sys.stderr, sample_rates
    end = time.time() - start
    print >>sys.stderr, 'time cost:'+str(end)

    sample_argument = list(itertools.repeat((samples, sample_rates), len(all_datasets)))
    start = time.time()
    offline_predicted_ratings = map(fillRatings, all_datasets, sample_argument)
    end = time.time() - start
    print >>sys.stderr, 'computing cost:'+str(end)

    tobeSorted = normMultiply(offline_predicted_ratings, exponentialized_offline_value, all_datasets)
    hasbeSorted = sorted(tobeSorted, key=lambda x: (x[0], x[1].ID), reverse=True)
    
    order = [getRating(b, raw_user_ratings) for b in hasbeSorted]
    return order
