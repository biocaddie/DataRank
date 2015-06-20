'''
Created on Jun 18, 2015

@author: arya
'''
class nameDB(object):
        def __init__(self):
            self.name=[]
            self.id=[]
        def insert(self,name):
            try:
                return self.name.index(name)
            except ValueError:
                self.name.append(name)
                self.id.append(len(self.id))
                return self.id[-1]
            
class MeSHDB(object):
    def __init__(self):
        self.entryTerm=nameDB()
        self.concept=nameDB()
        self.mesh=nameDB()

class PaperDB(object):
    def __init__(self):
        self.pmid=[]
        self.abstract=[]
        self.title=[]
        self.date=[]
        self.journal_id=[]
        self.owner_id =[]
        self.status_id=[]
        self.owner =nameDB()
        self.status=nameDB()
        

class JournalDB(object):
    def __init__(self):
        self.id=[]
        self.nlm_jid=[]
        self.name=[]
        self.date=[]
        self.journal_type_id=[]
        self.journal_country_id =[]
        self.language_id=[]
        self.journal_type=nameDB()
        self.journal_country =nameDB()
        self.language=nameDB()


class AuthorDB(object):
    def __init__(self):
        self.id=[]
        self.name=[]
        self.family=[]
        self.initial=[]

class DatasetDB(object):
    def __init__(self):
        self.id=[]
        self.accession=[]
        self.repository_id=[]
        self.repository=nameDB()
        
    def remove_duplicates(self):
        seen = set()
        seen_add = seen.add
        did,accession, repo_id=[],[],[]
        for i,a,r in zip(self.id,self.accession,self.repository_id):
            if not (i in seen or seen_add(i)):
                did.append(i)
                accession.append(a)
                repo_id =  self.repository.insert(r)
        self.id, self.accession, self.repository_id = did, accession, repo_id
        
    def insert(self,repository,accession):
        self.id.append(repository+'/' +accession)
        self.accession.append(accession)
        self.repository_id=self.repository.insert(repository)


class PaperAuthorDB:
    def __init__(self):
        self.id=[]
        self.author_id=[]
        self.paper_id=[]

class PaperMeshDB:
    def __init__(self):
        self.id=[]
        self.mesh_id=[]
        self.paper_id=[]
    

class PaperDatasetDB:
    def __init__(self):
        self.id=[]
        self.dataset_id=[]
        self.paper_id=[]
    
    def insert(self,paper_id,dataset_id):
        self.id.append(len(self.id))
        self.dataset_id.append(dataset_id)
        self.paper_id.append(paper_id)

class DatasetMeSHDB(object):
    def __init__(self):
        self.id=[]
        self.accession=[]
        self.repository_id=[]
        self.repository=nameDB()

class AuthorDatasetDB(object):
    def __init__(self):
        self.id=[]
        self.accession=[]
        self.repository_id=[]
        self.repository=nameDB()

class AuthorMeSHDB(object):
    def __init__(self):
        self.id=[]
        self.accession=[]
        self.repository_id=[]
        self.repository=nameDB()

class MEDLINEDatabase:
    def __init__(self):
        self.mesh=MeSHDB()
        self.paper=PaperDB()
        self.journal=JournalDB()
        self.author=AuthorDB()
        self.dataset=DatasetDB()
        self.paper_dataset=PaperDatasetDB()
        self.paper_author=PaperAuthorDB()
        self.paper_mesh=PaperMeshDB()

    def createMEDLINEDB(self,scriptPath='/home/arya/workspace/biocaddie/indexing/MEDLINE_create.sql',outPath='/home/arya/PubMed/MEDLINE.db'):
        import subprocess
        cmd= 'sqlite3 {} < {}'.format(outPath,scriptPath )
        subprocess.call(cmd,shell=True)