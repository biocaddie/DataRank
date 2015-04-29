import ast, itertools, sys, time, math
from multiprocessing import Pool
from search.models import *

RANKING_SIZE = 5000

# general algorithm is used to reduce #samples
def normList(alist_raw, func=lambda x: x, func2=lambda x: x):
    alist = [func2(a) for a in alist_raw]
    SUM = 1.*sum(alist)
    try:
        return [func(a/SUM) for a in alist]
    except ZeroDivisionError:
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
    n_jaccs = normList(jaccs, func=getLog)
    n_counts = normList(counts, func=getLog)
    results = [j+c for j, c in zip(*[n_jaccs, n_counts])]
    n_results_temp = normOnLog(results, func=getExp)
    n_results = normList(n_results_temp, getLog)
    lists = zip(*[n_results, datasets, n_jaccs, jaccs])
    return lists

def generalRanking(keywords):
    tmp = keywords.split('@')
    if len(tmp) == 2:
        keyw, datab = tuple(tmp)
    else:
        keyw = tmp[0]
        datab = ''
    free_text_query = keyw
    print >>sys.stderr, "keywords: "+str(keywords)

    if datab.strip().lower() == 'gse':
        datasets = Dataset.objects.filter(ID__startswith='GSE')[:RANKING_SIZE]
    elif datab.strip().lower() == 'genebank':
        datasets = Dataset.objects.filter().exclude(ID__startswith='GSE')[:RANKING_SIZE]
    else:
        datasets = Dataset.objects.all()[:RANKING_SIZE]
    print >>sys.stderr, "Read #lines: "+str(len(datasets))

    try:
        jaccs = [getSimilarity(free_text_query, st.Features) for st in datasets]
        counts = [st.Count for st in datasets]
        lists = normMultiply(jaccs, counts, datasets)
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
    size = len(sample_rates)*1.
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

def testRanking(offline_log_value, all_datasets, raw_user_ratings):
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
