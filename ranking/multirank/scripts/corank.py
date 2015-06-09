import sys, os, json, pdb, itertools
import pprint as pp
import datetime as dt
from collections import defaultdict, OrderedDict
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np
import scipy
from sklearn.preprocessing import normalize
# prints entire array
# np.set_printoptions(threshold=np.inf)


alpha = 0.1
lam = 0.2
eps = 0.0000000001
# implicit params for substeps
# n, m = 1, 1
# k_ = 1

def biwalk(U,V,x,k):
    c = x
    for i in xrange(k):
        b = U.T.dot(c)
        c = V.T.dot(b)
    b = U.T.dot(c)
    return b


def couplewalk(A_,D_,AD,DA,m,n,k,lam,eps):
    it = 0
    a = 1.0/len(author_list)*np.ones((len(author_list),1))
    d = 1.0/len(paper_list)*np.ones((len(paper_list),1))
    a_old = np.zeros((len(author_list),1))
    # # square A and D matrices, if n,m params > 1
    # temp_a = np.dot(A_.T, A_.T)
    # temp_d = np.dot(D_.T, D_.T)

    # while (not (a==a_old).all()) and (it <= 100):
    while (np.linalg.norm(a-a_old) >= eps  and (it <= 100)):
        print 'norm diff', np.linalg.norm(a-a_old)
        it += 1
        a_old = a
        d_old = d
        # http://stackoverflow.com/questions/24489285/segmentation-fault-on-ndarray-matrices-dot-product
        # a = (1-lam)*np.dot(np.linalg.matrix_power(A_.T,m),a_old) + lam*biwalk(DA,AD,d_old,k_)
        # d = (1-lam)*np.dot(np.linalg.matrix_power(D_.T,n),d_old) + lam*biwalk(AD,DA,a_old,k_)
        a = (1-lam)*np.dot(A_.T,a_old) + lam*biwalk(DA,AD,d_old,k_)
        d = (1-lam)*np.dot(D_.T,d_old) + lam*biwalk(AD,DA,a_old,k_)
        # a = (1-lam)*np.dot(temp_a,a_old) + lam*biwalk(DA,AD,d_old,k_)
        # d = (1-lam)*np.dot(temp_d,d_old) + lam*biwalk(AD,DA,a_old,k_)
        print 'while iteration', it
    return a,d

def make_ergodic(M, alpha, n_m):
    ones = np.ones((n_m,1))
    M_ = (1-alpha)*M + (alpha/n_m)*np.dot(ones, ones.T) 
    return M_


def check_stable(M_, iterations, eps=0.0000000001):
    m_ = np.ones(shape=(np.shape(M_)[0],1))*(1.0/np.shape(M_)[0])
    m = np.ones(shape=(np.shape(M_)[0],1))
    it = 0
    # while (not (m_ == m).all()) and (it <= iterations):
    while (np.linalg.norm(m_-m) >= eps and (it <= iterations)):
        if it % 50 == 0:
            print 'iteration', it
            print 'norm diff', np.linalg.norm(m_- m)
        it += 1
        m = m_
        m_ = np.dot(M_.T, m)
    print 'ran', it, 'iterations to stabilize...'
    return m_


# loads dictionaries to do stuff
execfile('multi_load_dicts.py')


### document citation network
def document_graph(cited_by, paper_list, paper_key):
    D = np.zeros(shape=(len(paper_list),len(paper_list)))
    for i in paper_list:
        if len(cited_by[i]) == 0:
            # not cited by docus in corpus
            D[paper_key[i]] = 1.0/len(paper_list)*np.ones((1,len(paper_list)))
        else:
            n_i = len(cited_by[i])
            temp_row = np.zeros((1,len(paper_list)))
            for j in cited_by[i]:
                temp_row[:,paper_key[j]] = 1.0/n_i
            D[paper_key[i]] = temp_row
    return D

# key is pmid, value is index of array
paper_key = dict((v,k) for k,v in dict(enumerate(paper_list)).items())


start = dt.datetime.now()
# stochastic matrix D for random walk on document network, G_D

# D = document_graph(cited_by, paper_list, paper_key)
D = document_graph(cites, paper_list, paper_key)

D_ = make_ergodic(D, alpha, len(paper_list))
end = dt.datetime.now()
print 'document transition matrix created...'
time_diff = divmod((end - start).total_seconds(), 60)
print 'elapsed time:', time_diff[1], 'sec ...'



start = dt.datetime.now()
d_ = check_stable(D_, 150)
end = dt.datetime.now()
time_diff = divmod((end - start).total_seconds(), 60)
print 'elapsed time (indiv doc ranking):', time_diff[1], 'sec ...'
d_norm1 = d_ / sum(d_)
d_idx1 = d_norm1.flatten().argsort()[::-1]




### author social network
# key is author, value is index of array
author_key = dict((v,k) for k,v in dict(enumerate(author_list)).items())

def author_graph(coauthors, author_paper, paper_author, n_A):
    rows_A, cols_A, T = [], [], []
    for i in coauthors.keys():
        coauths = coauthors[i].keys()
        coauths.append(i)
        for j in coauths:
            tau = []
            for e_k in author_paper[i]:
                if j in paper_author[e_k]:
                    tau.append(1.0 / (len(paper_author[e_k])*(len(paper_author[e_k])+1) * 0.5))
            rows_A.append(author_key[i])
            cols_A.append(author_key[j])
            T.append(sum(tau))
    singles = set(author_list) - set(coauthors.keys())
    for s in singles:
        rows_A.append(author_key[s])
        cols_A.append(author_key[s])
        T.append(1.0)
    return rows_A, cols_A, T


start = dt.datetime.now()
# stochastic matrix A for random walk on author network, G_A
rows_A, cols_A, T = author_graph(coauthors, author_paper, paper_author, len(author_list))
temp_A = scipy.sparse.csr_matrix((T, (rows_A, cols_A)), shape=(len(author_list), len(author_list)))

A = normalize(temp_A, norm='l1', axis=1)
A_ = make_ergodic(A, alpha, len(author_list))
end = dt.datetime.now()
print 'author transition matrix created...'
time_diff = divmod((end - start).total_seconds(), 60)
print 'elapsed time:', time_diff[1], 'sec ...'


start = dt.datetime.now()
a_ = check_stable(A_, 100, 0.000001)
end = dt.datetime.now()
time_diff = divmod((end - start).total_seconds(), 60)
print 'elapsed time (indiv author ranking):', time_diff[1], 'sec ...'
a_norm1 = a_ / sum(a_)
a_idx1 = np.array(a_norm1).flatten().argsort()[::-1]
# print 'author ranking for author random walk:'
# pp.pprint([author_list[i] for i in a_idx1[:15]])




### author-document bipartite graph

def bipartite_graph(paper_author, author_key, paper_key, paper_list):
    rows_E, cols_E, w = [], [], []
    # for p in paper_list:
    for j, authors in paper_author.items():
        if j in paper_key:
            for i in authors:
                rows_E.append(author_key[i])
                cols_E.append(paper_key[j])
                w.append(1.0 / len(authors))
    # weight matrix
    W = scipy.sparse.csr_matrix((w, (rows_E, cols_E)), shape=(len(author_list), len(paper_list)), dtype=float)
    denom = np.ravel(W.sum(axis=1))
    AD_ = []
    for idx,row in enumerate(rows_E):
        AD_.append(w[idx]*1.0/denom[row])
    AD = scipy.sparse.csr_matrix((AD_, (rows_E, cols_E)), shape=(len(author_list), len(paper_list)), dtype=float)
    DA = scipy.sparse.csr_matrix((w, (cols_E, rows_E)), shape=(len(paper_list), len(author_list)), dtype=float)
    return AD, DA

start = dt.datetime.now()
AD, DA = bipartite_graph(paper_author, author_key, paper_key, paper_list)
end = dt.datetime.now()
print 'document-author bipartite transition matrices created...'
time_diff = divmod((end - start).total_seconds(), 60)
print 'elapsed time:', time_diff[1], 'sec ...\n'




###### CO-RANK
start = dt.datetime.now()
a, d = couplewalk(A_,D_,AD,DA,m,n,k,lam,eps)
end = dt.datetime.now()
time_diff = divmod((end - start).total_seconds(), 60)
print 'elapsed time (coranking):', time_diff[1], 'sec ...\n'


d_norm2 = d / sum(d)
a_norm2 = a / sum(a)

# # # # (reverse) sort to get max index of normalized ranking vectors
d_idx2 = np.array(d_norm2).flatten().argsort()[::-1]
a_idx2 = np.array(a_norm2).flatten().argsort()[::-1]


# # # list top 10 rankings

print 'paper ranking after random walk on papers'
pp.pprint([str(paper_list[i])+' - '+str(len(cited_by[paper_list[i]])) for i in d_idx1[:15]])

print 'top 10 documents (corank)'
pp.pprint([str(paper_list[i])+' - '+str(len(cited_by[paper_list[i]])) for i in d_idx2[:15]])


print 'author ranking for author random walk:'
pp.pprint([author_list[i] for i in a_idx1[:15]])

print 'top 10 authors (corank)'
pp.pprint([author_list[i] for i in a_idx2[:15]])


# fout = open('out/docrank_may26.json','w')
# fout.write(json.dumps([paper_list[i] for i in d_idx1]))
# fout = open('out/corank_top_docs_may26.json','w')
# fout.write(json.dumps([paper_list[i] for i in d_idx2]))

# fout = open('out/authrank_may26.json','w')
# fout.write(json.dumps([author_list[i] for i in a_idx1]))
# fout = open('out/corank_top_authors_may26.json','w')
# fout.write(json.dumps([author_list[i] for i in a_idx2]))

# print 'exported top documents and authors...'
# fout.close()




# print results for report table
# indiv = [author_list[i] for i in a_idx1]
# corank = [author_list[i] for i in a_idx2]

# for i in indiv[:15]:
#     print i, str(len(set(author_paper[i]))), str(corank.index(i)+1)

# for c in corank[:15]:
#     print c, str(len(set(author_paper[c]))), str(indiv.index(c)+1)





## used this stuff to try to calculate some sort of loss function,
## not useful..

# def create_doc_ranking(doc_vals, doc_idx, paper_list, paper_to_dataset):
#     ranking = OrderedDict()
#     for idx, val in enumerate(doc_idx):
#         ranking[paper_list[val]] = {}
#         ranking[paper_list[val]]['rank'] = idx+1
#         ranking[paper_list[val]]['val'] = float(doc_vals[val])
#         ranking[paper_list[val]]['dataset'] = paper_to_dataset[paper_list[val]]
#     return ranking

# indep_doc_ranking = create_doc_ranking(d_norm1, d_idx1, paper_list, paper_to_dataset)
# corank_doc_ranking = create_doc_ranking(d_norm2, d_idx2, paper_list, paper_to_dataset)

# fout = open('out/docrank_top_docs_deg2_TEN.json','w')
# fout.write(json.dumps(indep_doc_ranking))
# fout = open('out/corank_top_docs_deg2_TEN.json','w')
# fout.write(json.dumps(corank_doc_ranking))

# def create_author_ranking(auth_vals, auth_idx, author_list, paper_to_dataset, author_paper):
#     ranking = OrderedDict()
#     for idx, val in enumerate(auth_idx):
#         ranking[author_list[val]] = {}
#         ranking[author_list[val]]['rank'] = idx+1
#         ranking[author_list[val]]['val'] = float(auth_vals[val])
#         dataset = []
#         for p in author_paper[author_list[val]]:
#             dataset.extend(paper_to_dataset[p])
#         ranking[author_list[val]]['dataset'] = list(set(dataset))
#     return ranking

# indep_auth_ranking = create_author_ranking(a_norm1, a_idx1, author_list, paper_to_dataset, author_paper)
# corank_auth_ranking = create_author_ranking(a_norm2, a_idx2, author_list, paper_to_dataset, author_paper)

# fout = open('out/authrank_top_authors_deg2_TEN.json','w')
# fout.write(json.dumps(indep_auth_ranking))
# fout = open('out/corank_top_authors_deg2_TEN.json','w')
# fout.write(json.dumps(corank_auth_ranking))

# print 'exported top documents and authors...'
# fout.close()