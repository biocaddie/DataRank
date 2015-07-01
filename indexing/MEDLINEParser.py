'''
Created on Jun 18, 2015

@author: arya
'''
from Bio import Entrez
import os
import numpy as np
import datetime
from multiprocessing import Pool
import pickle
import sys
import traceback




class MEDLINEParser:
    @staticmethod
    def MeSH(path='/home/arya/PubMed/MeSH/desc2015.xml'):
        from ParseMeSHXML import parse_mesh 
        from MEDLINEDatabase import MeSHDB
        records=parse_mesh(path)
        db=MeSHDB()
        for r in records:
            db.mesh.id.append(r.ui)
            db.mesh.name.append(r.name)
            for c in r.concepts:
                db.concept.id.append(c.ui)
                db.concept.name.append(c.name)
                for t in c.terms:
                    db.entryTerm.name.append(t.name)
                    db.entryTerm.id.append(t.ui)
        pickle.dump(db,open(path.replace('.xml','.pkl'),'wb'))
        pickle.dump({'uid':db.mesh.id,'name':db.mesh.name},open(path.replace('desc2015.xml','mesh.pkl'),'wb'))
        return db
        
    @staticmethod
    def mergeDatasetBatchResults(results):
        from MEDLINEDatabase import MEDLINEDatabase
        DB=MEDLINEDatabase()
        for db in results:
            DB.paper_dataset+=db.paper_dataset
            DB.dataset += db.dataset
        DB.dataset.remove_duplicates()
        return DB
    
    @staticmethod
    def Parse(path='/home/arya/PubMed/',num_threads=20, ParseFullMEDLINE=True):
        """
        if ParseFullMEDLINE=True: it parses all the fields in the MEDLINE records
        else: it only looks for datasets
        """
#     f = Entrez.efetch(db='pubmed',id='10540283', retmode="xml")
#     records = Entrez.parse(f)
        num_batches = max(map(lambda x: int(x.split('_')[1].split('.')[0]),[ f for f in os.listdir(path+'MEDLINE/raw/') if os.path.isfile(os.path.join(path+'MEDLINE/raw/',f)) ]))+1
        fileout=path+'Datasets/{}.pkl'.format(('datasets','MEDLINE')[ParseFullMEDLINE])
        sys.stdout = open(fileout.replace('.pkl','.log'),'w')
        sys.stderr = open(fileout.replace('.pkl','.err'),'w')
        start=0
        pool = Pool(num_threads)
        if ParseFullMEDLINE:
            meshdb=MEDLINEParser.MeSH()
            param=[{'path':path+'MEDLINE/raw/batch_{}.xml'.format(j), 'meshdb':meshdb} for j in range(start, num_batches)]
            db=pool.map(parseBatchMEDLINE_helper,param)
        else:
            param=[{'path':path+'MEDLINE/raw/batch_{}.xml'.format(j) for j in range(start, num_batches)}]
            db=pool.map(parseBatchDataset_helper,param)
        pool.terminate()
        print '\nMerging...\n'
        db = MEDLINEParser.mergeDatasetBatchResults(db)
#         MEDLINEParser.dataset_stats( data=db)
        pickle.dump(db,open(fileout,'w'))
        
                
    @staticmethod
    def dataset_stats(path=None, data=None):
        if data is None:    data=pickle.load(open(path))
        else: data['iter']=0
        db=data['db']
        print  '************************************************'
        print  '{:20}{:10}{:10}'.format('Repository','#Datasets', '#Uniques')
        
        
        rd = sorted(map(lambda (k,v): (k,len(v),len(set(v))),data['RD'].items()),key=lambda x: x[1],reverse=True)
        for [k,u,v] in rd:    print  '{:20}{:10}{:10}'.format(k,u,v)
        print  '-------------------------------\n{:20}{:10}{:10}\n'.format('Total',sum(map(lambda (k,u,v):u,rd)),sum(map(lambda (k,u,v):v,rd)))
        print  'Until Batch {:5}, {:7} datasets are found {:7} papers'.format(data['iter'], sum(map(len,data['PD'].values())),len(data['PD'].keys())) 
        
    @staticmethod
    def parseBatchDataset(path):
        from MEDLINEDatabase import MEDLINEDatabase
        db=MEDLINEDatabase()
        f=open(path)
        try:
            records = Entrez.parse(f)
            for record in records:
                if 'MedlineCitation' in record.keys():
                    rec=record['MedlineCitation']
                    if 'Article' in rec.keys():
                        if 'DataBankList' in rec['Article'].keys():
                            for d in rec['Article']['DataBankList']:
                                for a in d['AccessionNumberList']:
                                    accession=str.decode(a,'unicode-escape')
                                    repository = str.decode(d['DataBankName'],'unicode-escape')
                                    db.dataset.insert(repository, accession)
                                    paper_id=str(rec['PMID'])
                                    db.paper_dataset.insert( paper_id, db.dataset.id[-1])
        except:
            print >> sys.stderr, '{}\n{}\n***********'.format(path,traceback.format_exc())
        print path 
        sys.stdout.flush()
        return db
    
    @staticmethod
    def parseBatchMEDLINE(path,meshdb):
        f=open(path)
        try:
            records = Entrez.parse(f)
            for record in records:
                if 'MedlineCitation' in record.keys():
                    rec=record['MedlineCitation']
                    if 'Article' in rec.keys():
                        if 'DataBankList' in rec['Article'].keys():
                            for d in rec['Article']['DataBankList']:
                                for a in d['AccessionNumberList']:
                                    accession=str.decode(a,'unicode-escape')
                                    repository = str.decode(d['DataBankName'],'unicode-escape')
                                    val=repository+'/'+accession
        except:
            print >> sys.stderr, '{}\n{}\n***********'.format(path,traceback.format_exc())
        print path 
        sys.stdout.flush()
    
def parseBatchMEDLINE_helper(param):
    return MEDLINEParser.parseBatchMEDLINE(**param)    

def parseBatchDataset_helper(param):
    return MEDLINEParser.parseBatchDataset(**param)


if __name__ == '__main__':
    from time import time
    s=time()
#     MEDLINEParser.Parse(ParseFullMEDLINE = False)
    MEDLINEParser.Parse(path='/home/arya/PubMed/GEO/')
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)
