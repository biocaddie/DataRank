'''
Created on Jul 3, 2015

@author: arya
'''
import numpy as np
def AP(ranking, targets, k=25):
    """average precision"""
    ranking=np.array(ranking[:k])
    results=np.array([])
    for tt in targets:
        results =np.append(results, np.where(ranking==tt)[0])
    results +=1
    print '{} hits in top {}'.format(len(results),k)
    return  len(results)/float(k)
        

def MRR(ranking, targets, k=20):
    """mean reciprocal rank"""
    """average precision"""
    ranking=np.array(ranking[:k])
    results=np.array([])
    for tt in targets:
        results =np.append(results, np.where(ranking==tt)[0])
    if len(results):
        results +=1
        print '{} is 1st hit in top {}'.format(min(results),k)
        return  1.0/min(results)
    else:
        print 'No hit in top',k
        return 0
    
if __name__ == '__main__':
    pass