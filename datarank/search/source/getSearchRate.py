from search.models import SearchRate, Dataset

session = "10/03/2015,07:25:04"
def getInfos(session):
    datas = SearchRate.objects.filter(sessioncreated__startswith=session)
    print "#steps: "+str(len(datas))
    return [data.ratings for data in datas]
def getLatestInfo(user, num=10):
    datas = SearchRate.objects.filter(username=user)
    size = len(datas)
    for data in datas[size-num:size]:
        print '\n'+data.keywords+', '+data.sessioncreated+'\n '+data.ratings
def saveInfo(session):
    ratings_rounds = getInfos(session)
    # print "#steps: "+str(len(ratings_rounds))
    return ratings_rounds

def saveInfo2(fname):
    datas = Dataset.objects.all()[:5000]
    ratings_rounds = [data.ID for data in datas]
    print "#size: "+str(len(ratings_rounds))
    with open('search/data/'+fname, 'w') as f:
        f.write(str(ratings_rounds)+'\n')

with open('search/data/allids') as f:
    keys = eval(f.read().split('\n')[0])

def getKeys(session, fname):
    datas = saveInfo(session)
    print "#size: "+str(len(datas))
    results = []
    for ind, line in enumerate(datas):
        dic = eval(line)
        # print type(dic)
        tmp_dict = dict(zip(keys, [0] * len(keys)))
        for key, value in dic.iteritems():
            tmp_dict[key] = value
        results.append(tmp_dict.values())
    with open('search/data/'+fname, 'w') as f:
        for re in results:
            f.write(str(re)+'\n')

# saveInfo('10/03/2015,07:35:22', 'first')
getKeys('11/03/2015,21:22:01', 'amir')
