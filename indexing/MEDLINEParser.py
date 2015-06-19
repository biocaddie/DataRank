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
def add_record(param,record):
    param['pmid'].append(record['MedlineCitation']['PMID'])
    try:
        param['abstract'].append(record['MedlineCitation']['Article']['Abstract']['AbstractText'][0])
        param['abstractLength'].append(len(record['MedlineCitation']['Article']['Abstract']['AbstractText'][0]))
    except KeyError:
        param['abstract'].append('')
        param['abstractLength'].append(0)
    param['DataBankList'].append(record['MedlineCitation']['Article']['DataBankList'])
    param['title'].append(record['MedlineCitation']['Article']['ArticleTitle'])
    param['date'].append(record['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'])
    param['lang'].append(record['MedlineCitation']['Article']['Language'])
    param['mesh'].append(record['MedlineCitation']['MeshHeadingList'])
    param['author'].append(record['MedlineCitation']['Article']['AuthorList'][0])
    param['journal'].append(record['MedlineCitation']['MedlineJournalInfo']['MedlineTA'])
    param['country'].append(record['MedlineCitation']['MedlineJournalInfo']['Country'])
    param['jid'].append(record['MedlineCitation']['MedlineJournalInfo']['NlmUniqueID'])
    param['issn'].append(record['MedlineCitation']['MedlineJournalInfo']['ISSNLinking'])




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
        return db
        
    @staticmethod
    def mergeDatasetBatchResults(results):
        PD,RD={},{}
        for batch in results:
            PD.update(batch['PD'])
            for k,v in batch['RD'].items():
                if k in RD.keys():
                    for i in v:
                        RD[k].append(i)
                else:
                    RD[k]=v
        return {'PD':PD,'RD':RD}
    
    @staticmethod
    def Parse(path='/home/arya/PubMed/',num_threads=20, ParseFullMEDLINE=True):
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
            param=[path+'MEDLINE/raw/batch_{}.xml'.format(j) for j in range(start, num_batches)]
            db=pool.map(parseBatchDataset_helper,param)
        pool.terminate()
        print '\nMerging...\n'
        db = MEDLINEParser.mergeDatasetBatchResults(db)
        MEDLINEParser.dataset_stats( data=db)
        pickle.dump(db,open(fileout,'w'))
        
        
        

                

    @staticmethod
    def dataset_stats(path=None, data=None):
        if data is None:    data=pickle.load(open(path))
        else: data['iter']=0
    #     with open(path.replace('.pkl','.log'),'a') as f:
        print  '************************************************'
        print  '{:20}{:10}{:10}'.format('Repository','#Datasets', '#Uniques')
        rd = sorted(map(lambda (k,v): (k,len(v),len(set(v))),data['RD'].items()),key=lambda x: x[1],reverse=True)
        for [k,u,v] in rd:    print  '{:20}{:10}{:10}'.format(k,u,v)
        print  '-------------------------------\n{:20}{:10}{:10}\n'.format('Total',sum(map(lambda (k,u,v):u,rd)),sum(map(lambda (k,u,v):v,rd)))
        print  'Until Batch {:5}, {:7} datasets are found {:7} papers'.format(data['iter'], sum(map(len,data['PD'].values())),len(data['PD'].keys()))
    
    
    @staticmethod
    def parseBatchDataset(path):
#         PD,RD={},{}
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
                                    val=repository+'/'+accession
                                    try:
                                        db.paper_dataset[str(rec['PMID'])].append(val)
#                                         PD[str(rec['PMID'])].append(val)
                                    except:
                                        db.paper_dataset[str(rec['PMID'])]=[val]
#                                         PD[str(rec['PMID'])]=[val]
                                    if repository not in db.dataset.repository.name: 
                                        db.dataset.repository.name
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
                                    try:
#                                         PD[str(rec['PMID'])].append(val)
                                    except:
#                                         PD[str(rec['PMID'])]=[val]
                                    try:
#                                         RD[repository].append(accession)
                                    except:
#                                         RD[repository]=[accession]
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
    
    MEDLINEParser.Parse()
    
    print 'Done in {:.0f} minutes!'.format((time()-s)/60)
