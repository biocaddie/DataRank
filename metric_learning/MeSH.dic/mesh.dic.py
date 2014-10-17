dic=[]
import json
from os import listdir
from os.path import isfile, join

path='/home/public/MeSH/medlease.json/'
path='/home/public/MeSH/medleasebaseline.json/'
files = [ f for f in listdir(path) if isfile(join(path,f)) ]
 
j=0
for f in files:
    j+=1
    jfile=open(path+f)
    data=json.load(jfile)
    i=0
    with open('/home/airanmehr/mesh.out','w') as ofile:
	       print >> ofile,j
    for item in data:
        for (year, recs) in item.items():
            for (p,mesh) in recs.items():
                for meshterm in mesh.keys():
                    i+=1
                    terms= meshterm.split(' ') 
                    for w in terms:
                        if w.lower() not in dic:
                            dic.append(w.lower())
                      
        break
    print 'Num of MeSH ={0}, length of Dic = {1}'.format(i, len(dic))
with open('/home/airanmehr/mesh2.dict','w') as dicfile:
    for w in dic:
        print >> dicfile,w

