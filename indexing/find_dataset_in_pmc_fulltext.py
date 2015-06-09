'''
Created on Dec 22, 2014
@author: WeiWei
'''
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import sqlite3 as sq
import os, re,pickle,platform

class DataSetFinder(object):
    '''
    This class searches pre-selected batch files with query strings. Locate the string and associated article PMIDs
    '''
    def __init__(self, fileName, pattern, outputDir):
        self.xmlFile = fileName
        self.pattern = pattern
        self.results = {}
        self.outDir = outputDir
    def xmlParser(self):
        raw = file(self.xmlFile).read()
#         xmlDoc = raw.encode("cp8","ignore")
        xmlDoc = raw.encode('utf-8','ignore')
        
        soup = bs(xmlDoc,"xml")
        articleList = soup.find_all("article")
        for article in articleList:
            text = article.get_text()
            if re.search(self.pattern,text): 
                # pattern Genbank accession no. U93237
                try:             
                    pmid = article.find_all("article-id",{"pub-id-type":"pmid"})[0].get_text()
                    dataset=re.findall(self.pattern, text)
                    self.results[pmid]=dataset
                    print pmid, dataset
                except:
                    pass
        self.output()
    def validate(self):
        pass
    
    def output(self):
        pickle.dump(self.results,file(self.outDir,"w"))

def loadData(bashoutDir):
    """Parse out files from search results; prepare a list of file names"""
    genbankRaw = file(os.path.join(bashoutDir,"GenBank_accession.out")).readlines()
    genbankFiles = [x[:-1].split("./")[1] for x in genbankRaw]
    return genbankFiles

def main():
    if platform.system()=="Linux":
        bashoutDir = "/home/PubMed/searchResults"
        dataDir = loadData(bashoutDir)
        wkdir = "/home/PubMed/PMC_XML"
    elif platform.system()=="Windows":
        bashoutDir = r"C:\Users\WeiWei\Dropbox\Research\biocaddie\experiments\searchResults"
        dataDir = ["PMC_batch1652.xml"]
        wkdir = r"C:\Users\WeiWei\Dropbox\Research\biocaddie\data"
    
    
    genbank_pattern  = re.compile("(GenBank accession).* ([a-zA-Z]{1,5}[0-9]{2,8})", re.I)

    geo_pattern = re.compile("(GEO)? (accession)?.*(GSE[0-9]+)|\
                              (GEO)? (accession)?.*(GPL[0-9]+)|\
                              (GEO)? (accession)?.*(GDS[0-9]+)|\
                              (GEO)? (accession)?.*(GSM[0-9]+)|\
                              http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE", re.IGNORECASE) 
    outdir = "genbank.pkl"
    print "Search for genbank"
    for xml in dataDir:
        xmlFile = os.path.join(wkdir,xml)
        finder = DataSetFinder(xmlFile, genbank_pattern,outdir)
        finder.xmlParser()

main()