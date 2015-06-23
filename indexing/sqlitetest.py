import os
import sqlite3
import re
import mechanize
import urllib2
from Bio import Entrez
from bs4 import BeautifulSoup
import MEDLINEServer


def _getResultURL(mode,text):
    #the search page of web of science
    searchURL = "http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=2AkR6Gt4nU7x1c8tniD&preferencesSaved="
    br = mechanize.Browser()
    br.open(searchURL)
    br.select_form(name="UA_GeneralSearch_input_form")
    br.form["value(input1)"]=text
    controlItem = br.form.find_control("value(select1)",type="select")
    if mode == 1:
        controlItem.value = ['DO']
    elif mode == 2:
        print "using title to search"
        controlItem.value = ['TI']
    request = br.form.click()
    response = mechanize.urlopen(request)
    return response.geturl()

def nextPageExist(soup):
    lists = soup.find("a",attrs={"class": "paginationNext"})
    if lists['href'] == "javascript: void(0)":
        return None
    else:
        return lists['href']

def _addCitaLists(pmid,url):
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    firsttime = True
    nexturl = nextPageExist(soup)
    titles=[]
    while firsttime or nexturl is not None:
        lists = soup.find_all("div", class_="search-results-content")
        for tag in lists:
            titles.append(tag.find("value",attrs={"lang_id": ""}).get_text().strip())
        if firsttime and nexturl is not None:
            soup = BeautifulSoup(urllib2.urlopen(nexturl).read())
            firsttime = False
        elif firsttime and nexturl is None:
            break
        else:
            nexturl = nextPageExist(soup)
            if nexturl is not None:
                soup = BeautifulSoup(urllib2.urlopen(nexturl).read())
                firsttime = False
    return titles

def _parseURL(pmid,reURL):
    contents = urllib2.urlopen(reURL).read()
    soup = BeautifulSoup(contents)
    URL = soup.find("a",attrs={"class": "smallV110"})#only one result normally
    if URL is not None:
        url = "http://apps.webofknowledge.com"+URL['href']
        contents2 = urllib2.urlopen(url).read()
        soup2 = BeautifulSoup(contents2)
        citedlists2 = soup2.find("a",attrs={"title": "View all of the articles that cite this one"})
        if citedlists2 is not None:
            ciurl2 = "http://apps.webofknowledge.com" + citedlists2['href']
            _addCitaLists(pmid,ciurl2)
    else:
        print "Cannot find the data of PMID =",pmid


def citationNetwork(pmidList, titleList, doiList):
    for (pmid,title,doi) in zip(pmidList, titleList, doiList):
        if doi:
            print "doi searching+++++++"
            reURL = _getResultURL(1,doi)
            print pmid,reURL
            if reURL is not None:
                _parseURL(pmid,reURL)
        elif title:
            print "title searching"
            reURL = _getResultURL(2,title)
            print pmid,reURL
            if reURL is not None:
                _parseURL(pmid,reURL)
        else:
            print "Cannot find the data of PMID =",pmid

def remove_None(seq):
    return [x for x in seq if x is not None]

if __name__ == '__main__':
    import pickle
    pmidList= MEDLINEServer.MEDLINEServer.loadPMIDs('/Users/arya/')
    PT=pickle.load(open('/Users/arya/PT.pkl'))
    PDOI=pickle.load(open('/Users/arya/PDOI.pkl'))
    titleList=[]
    doiList=[]
    for pmid in pmidList:
        titleList.append(PT[pmid])
        doiList.append(PDOI[pmid])
    print doiList[:10]
    exit()
    print len(pmidList),len(titleList),len(doiList)
    print len(remove_None(pmidList)),len(remove_None(titleList)),len(remove_None(doiList))
    citationNetwork(pmidList, titleList, doiList)

