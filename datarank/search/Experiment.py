from search.models import SearchRate, Dataset
from django.conf import settings
import time, os

def write2log(rate):
    result = {}
    result['user'] = rate.username
    result['keyw'] = rate.keywords
    result['session'] = rate.sessioncreated
    # result['rating'] = rate.ratings
    with open(os.path.join(settings.BASE_DIR ,'search/experData/log'), 'a+') as f:
        f.write(str(result)+'\n')
    return

def write2file(fname, rate):
    result = {}
    result['user'] = rate.username
    result['keyw'] = rate.keywords
    result['session'] = rate.sessioncreated
    result['rating'] = rate.ratings

    print "Writing Experiment Data"
    with open(os.path.join(settings.BASE_DIR ,'search/experData/'+fname+'__ratings'), 'a+') as f:
        f.write(result['rating']+"\n")

    with open(os.path.join(settings.BASE_DIR ,'search/data/allids')) as f:
        keys = eval(f.read().split('\n')[0])
    tmp_dict = dict(zip(keys, [0] * len(keys)))
    rating_dict = eval(result['rating'])
    for key, value in rating_dict.iteritems():
        tmp_dict[key] = value
    with open(os.path.join(settings.BASE_DIR ,'search/experData/'+fname+'__vectors'), 'a+') as f:
        f.write(str(tmp_dict.values())+"\n")

def write2file_predratings(fname, id2rating):
    with open(os.path.join(settings.BASE_DIR ,'search/data/allids')) as f:
        keys = eval(f.read().split('\n')[0])
    tmp_dict = dict(zip(keys, [0] * len(keys)))
    for key, value in id2rating.iteritems():
        tmp_dict[key] = value
    with open(os.path.join(settings.BASE_DIR ,'search/experData/'+fname+'__predRatings'), 'a+') as f:
        f.write(str(tmp_dict.values())+"\n")

# write2file('test2')
