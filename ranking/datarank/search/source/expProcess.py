def get_kappa(A=None,B=None):
    from pandas import crosstab
    import numpy as np
    A = np.array(A)
    print np.histogram(A, range(6))
    B = np.array(B)
    if A is None or B is None:
        k=5
        n=30
        A=np.array([np.random.randint(k)+1 for _ in range(n)])
        B=np.array([np.random.randint(k)+1 for _ in range(n)])
        ## Wikipedia Example 1
        A= np.append(np.zeros(25, dtype=int),np.ones(25, dtype=int))
        B= np.roll(np.append(np.zeros(30, dtype=int),np.ones(20, dtype=int)), 5)
       
#         ## Wikipedia Example 2
#         A= np.append(np.zeros(60, dtype=int),np.ones(40, dtype=int))
#         B= np.roll(np.append(np.zeros(70, dtype=int),np.ones(30, dtype=int)), 15)
#        
#         ## Wikipedia Example 3
#         A= np.append(np.zeros(60, dtype=int),np.ones(40, dtype=int))
#         B= np.roll(np.append(np.zeros(30, dtype=int),np.ones(70, dtype=int)), -5)
       
       
#         print 'A',A
#         print 'B', B
   
    T=crosstab(A,B,rownames='A',colnames='B').as_matrix()
    print T.shape
    print T
    b= T.sum(0)
    a= T.sum(1)
    p=T.diagonal().sum()/float(T.sum())
    b=b/float(b.sum())
    a=a/float(a.sum())
    print a.shape
    print b.shape
    e= sum(a*b)
#     e=sum((T.diagonal()/float(T.sum()))**2) ## xiaoqian's xls file
   
    kappa= (p-e)/(1-e)
    print 'kappa:', kappa
    return kappa

with open('../data/allids') as f:
    keys = eval(f.read().split('\n')[0])
    # print type(keys)
    # print keys[:20]

def getKeys(fname):
    with open('../experData/'+fname) as f:
        datas = f.read().split('\n')[:-1]
        results = [eval(data) for data in datas]
    return results

results = getKeys('huw12_03_2015_02_52_30__vectors')
print len(results)
print len(results[0])
print len(results[1])
print len(results[2])
print len(results[3])
for i in range(len(results)-1):
    print 'round: '+str(i)
    get_kappa(A=results[i], B=results[i+1])
