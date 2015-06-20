### reads dictionaries and creates matlab variables for subs,vars to run demo.m
### subs is coordinate of nonzero, vars is nonzero value



import sys, os, json, pdb, itertools
import pprint as pp
import datetime as dt
from collections import defaultdict
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np
import scipy


execfile('multi_load_dicts.py')

# available dicts:
# author_paper
# paper_author
# paper_journal
# journal_paper
# cites: cites[a] = [b,c,d] --> means b,c,d cites a

paper_key = dict((v,k) for k,v in dict(enumerate(paper_list, start=1)).items())
author_key = dict((v,k) for k,v in dict(enumerate(author_list, start=1)).items())
journal_key = dict((v,k) for k,v in dict(enumerate(journal_list, start=1)).items())
datasets = b_cancer.keys()
dataset_key = dict((v,k) for k,v in dict(enumerate(datasets, start=1)).items())


# A = np.zeros(shape=(len(author_key)+1, len(author_key)+1, len(journal_key)+1))
# for j in journal_paper:
#     j_slice = A[:,:,journal_key[j]]
#     for i1 in journal_paper[j]: # for pairs of papers (i1,i2) both of journal j
#         for i2 in journal_paper[j]:
#             if (i1 != i2) and (i1 in cites[i2]) and (i1 in paper_key) and (i2 in paper_key):
#                 # print i1, i2, j
#                 # break
#                 # if i1 cites i2, then a1 authors cite a2
#                 a1 = reduce(lambda l, i: l + i, [[item] * len(paper_author[i2]) for item in paper_author[i1]])
#                 a2 = paper_author[i2] * len(paper_author[i1])
#                 links = zip(a1, a2)
#                 for l in links:
#                     j_slice[author_key[l[0]]][author_key[l[1]]] = 1
#     print 'sum of citations', sum(sum(j_slice))
#     A[:,:,journal_key[j]] = j_slice
# print 'created A...'


#### # convert A to format for matlab export
# nz = np.nonzero(A)
# print 'found non-zeros of A...'

# sub = list('subs = [')
# for s in zip(nz[0],nz[1],nz[2])
#     sub.extend([str(s[0]), ' ', str(s[1]), ' ', str(s[2]), '; '])

# sub[-1] = '];'
# subs = ''.join(sub)

# data = A[nz]
# val = list('vals = [')
# for d in data:
#     val.extend([str(d), '; '])

# val[-1] = '];'
# vals = ''.join(val)

# fout = open('load_A.m', 'w+')
# fout.write(subs+'\n')
# fout.write(vals+'\n')
# fout.close()
# print 'exported A to matlab tensor format :)'


### exports the paper,author,journal dictionaries to matlab

# import scipy.io
# a_idx = []
# a_names = []
# for k,v in author_key.items():
#     a_names.append(k)
#     a_idx.append(v)

# names_list = np.zeros((len(a_names),), dtype=np.object)
# names_list[:] = a_names
# scipy.io.savemat('a_names.mat', mdict={'names_list': names_list})
# scipy.io.savemat('a_idx.mat', mdict={'a_idx': a_idx})

# j_idx = []
# j_names = []
# for k,v in journal_key.items():
#     j_idx.append(v)
#     j_names.append(k)

# j_list = np.zeros((len(j_names),), dtype=np.object)
# j_list[:] = j_names
# scipy.io.savemat('j_names.mat', mdict={'j_list': j_list})
# scipy.io.savemat('j_idx.mat', mdict={'j_idx': j_idx})

# d_idx = []
# d_names = []
# for k,v in dataset_key.items():
#     d_names.append(k)
#     d_idx.append(v)

# dataset_list = np.zeros((len(d_names),), dtype=np.object)
# dataset_list[:] = d_names
# scipy.io.savemat('d_names.mat', mdict={'dataset_list': dataset_list})
# scipy.io.savemat('d_idx.mat', mdict={'d_idx': d_idx})

















########################
### testing some calculations for cond prob to try

# JD = np.zeros(shape=(len(journal_key)+1, len(dataset_key)+1))

# for j in journal_key:
#     weight = [0] * (len(dataset_key)+1)
#     datas = 0
#     papers = journal_paper[j]
#     for p in papers:
#         datas += len(paper_to_dataset[p])
#         for d in paper_to_dataset[p]:
#             weight[dataset_key[d]] += 1
#     # print 'check', sum(weight) == datas
#     JD[journal_key[j],:] = weight


# JD_norm = np.zeros(shape=(len(journal_key)+1, len(dataset_key)+1))
# denom = JD.sum(axis=1)

# # for i in xrange(1,len(journal_key)+1):
# #     JD_norm[i,:] = JD[i,:] / denom[i]

# scipy.io.savemat('JD.mat', mdict={'JD':JD})


# AJ1 = [0] * (len(author_key)+1)
# AJ1[0] = [0]*(len(journal_key)+1)

# for a in author_key:
#     j = [0]*(len(journal_key)+1)
#     for p in author_paper[a]:
#         j_idx = journal_key[paper_journal[p]]
#         j[j_idx] += 1
#     AJ1[author_key[a]] = j

# AJ = np.asarray(AJ1, dtype=float)

# scipy.io.savemat('AJ.mat', mdict={'AJ':AJ})

