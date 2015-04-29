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
    # for xx in x:
    #     print >>sys.stderr, xx

    y_raw = dataset2.split(';')
    y_r2 = [d.strip() for d in y_raw]
    y = set(y_r2)
    # for yy in y:
    #     print >>sys.stderr, yy
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
    # datasets = Dataset.objects.all()
    print >>sys.stderr, "Read #lines: "+str(len(datasets))

    try:
        # lists = [(getSimilarity(base, set.Features), set) for set in datasets]
        jaccs = [getSimilarity(free_text_query, st.Features) for st in datasets]
        # n_jaccs = normList(jaccs, func=getLog)
        # print >>sys.stderr, n_jaccs[:5]

        counts = [st.Count for st in datasets]
        # print >>sys.stderr, counts[:5]
        # n_counts = normList(counts, func=getLog)
        # print >>sys.stderr, n_counts[:5]

        # WE ARE IN LOG SCALE!!!
        # results = [j+c for j, c in zip(*[n_jaccs, n_counts])]
        # print >>sys.stderr, results[:5]
        # n_results_temp = normOnLog(results, func=getExp)
        # print >>sys.stderr, n_results_temp[:5]
        # n_results = normList(n_results_temp, getLog)
        # print >>sys.stderr, n_results[:5]
        # print >>sys.stderr, max(n_results)

        # lists = zip(*[n_results, datasets, n_jaccs, jaccs])
        lists = normMultiply(jaccs, counts, datasets)
    except ValueError:
        return None
    # except ZeroDivisionError:
    #     return None
    sort = sorted(lists, key=lambda x: (x[0], x[1].ID), reverse=True)
    # lists = [s[1] for s in sort]
    # return lists[:RANKING_SIZE]
    # return lists
    # print >>sys.stderr, '>>>General test: '+str(sort[0][1].ID)
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
        # print >>sys.stderr, 'sammmmmmmmmmmm:'+str(ind)
        # print >>sys.stderr, 'sammmmmmmmmmmm:'+str(dataset.ID)
        rate = sample_rates[ind]
        # print >>sys.stderr, 'sammmmmmmmmmmm:'+str(rate)
        sum_dist = 1
    #    result = rate
    except ValueError:
        dists = [getSimilarity(dataset.Features, sample.Features) for sample in samples]
        # print >>sys.stderr, 'sammmmmm:'+str(len(dists))
        rate = sum([d*r for d,r in zip(dists, sample_rates)])
        # print >>sys.stderr, 'sammmmmm:'+str(rate)
        # sum_dist = 1. * sum(dists)
        sum_dist = 1. * size
    #    result = rate / sum_dist
    # print >>sys.stderr, 'samm:'+str(rate)
    # print >>sys.stderr, 'samm:'+str(sum_dist)
    try:
        result = rate / sum_dist
    except ZeroDivisionError:
        result = 1e-200
    # print >>sys.stderr, 'samm:'+str(result)
    # if dataset in samples:
    #     print >>sys.stderr, '#samples '+str(len(samples))
    #     print >>sys.stderr, 'samples rates'+str(sample_rates)
    #     print >>sys.stderr, 'sample id '+str(samples[0].ID)
    #     print >>sys.stderr, 'dists'+str(dists)
    #     print >>sys.stderr, 'final rate'+str(rate)
    #     print >>sys.stderr, 'n_dist'+str(conf)
    #     print >>sys.stderr, '-------------'
    return result

def testRanking(offline_log_value, all_datasets, raw_user_ratings):
    # print >> sys.stderr, rs[0]
    # print >> sys.stderr, base[0].ID
    exponentialized_offline_value = [getExp(r) for r in offline_log_value]
    raw_user_ratings = ast.literal_eval(raw_user_ratings)
    # print >>sys.stderr, '>>>>TestRanking Test: '+str(ratings)
    
    start = time.time()
    samples, sample_rates = zip(*[(Dataset.objects.get(ID=key), float(value)) for key,value in raw_user_ratings.iteritems() if value != '0'])
    print >> sys.stderr, len(samples)
    print >> sys.stderr, sample_rates

    # print >>sys.stderr, '>>>>TestRanking Test: '+str(len(samples))
    # print >>sys.stderr, '>>>>TestRanking Test: '+str(sample_rates)
    # print >>sys.stderr, '>>>>TestRanking Test: '+str(len(sample_rates))
    # print >>sys.stderr, '>>>>TestRanking Test: '+str(sample_rates[0])
    
    end = time.time() - start
    print >>sys.stderr, 'time cost:'+str(end)

    
    # p = Pool(5)
    sample_argument = list(itertools.repeat((samples, sample_rates), len(all_datasets)))
    start = time.time()
    offline_predicted_ratings = map(fillRatings, all_datasets, sample_argument)
    # print >> sys.stderr, rating_tmp[0]
    # print >> sys.stderr, max(rating_tmp)
    # print >> sys.stderr, rs[0]
    # tobeSorted = [(fillRatings(d, samples, sample_rates), d) for d in base]
    end = time.time() - start
    print >>sys.stderr, 'computing cost:'+str(end)
    # tobeSorted = zip(*[rating_tmp, base])

    tobeSorted = normMultiply(offline_predicted_ratings, exponentialized_offline_value, all_datasets)
    # print >> sys.stderr, tobeSorted[0][0]
    # print >> sys.stderr, tobeSorted[1][0]
    # print >> sys.stderr, tobeSorted[3][0]
    # print >> sys.stderr, tobeSorted[0][1].ID
    # lists = zip(*[n_results, datasets, n_jaccs, jaccs])
    # preds, _, log_filling, filling = zip(*lists)

    hasbeSorted = sorted(tobeSorted, key=lambda x: (x[0], x[1].ID), reverse=True)
    
    order = [getRating(b, raw_user_ratings) for b in hasbeSorted]
    return order
