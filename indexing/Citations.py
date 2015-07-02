import os
import sys
import pickle
import multiprocessing
import re
import mechanize
import urllib2
from bs4 import BeautifulSoup
import MEDLINEServer
path='/home/arya/PubMed/GEO/'   
citations_path=path+'Citations/'
if not os.path.exists(citations_path):            os.makedirs(citations_path)

def _getResultURL(mode,text):
    #the search page of web of science
    searchURL = "http://www.webofknowledge.com/?"
#     searchURL = 'http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=1C8JxbKLQCxk9XJveW5&preferencesSaved='
    br = mechanize.Browser()
    br.open(searchURL)
    br.select_form(name="UA_GeneralSearch_input_form")
    br.form["value(input1)"]=text
    controlItem = br.form.find_control("value(select1)",type="select")
    if mode == 1:
        controlItem.value = ['DO']
    elif mode == 2:
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
    while firsttime or nexturl is not None:
        lists = soup.find_all("div", class_="search-results-content")
        for tag in lists:
            title = tag.find("value",attrs={"lang_id": ""}).get_text().strip()
            authorss = tag.find("span",text=re.compile("By: "))
            if authorss is not None:
                authors = authorss.parent.get_text().strip()[4:]
            else:
                authors = ""
            journal = tag.find("source_title_txt_label").get_text().strip()
            date = tag.find(text=re.compile("Published: ")).next_element.get_text()
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


def get_citations_doi_pmid(citations_page_url):
    soup = BeautifulSoup(urllib2.urlopen(citations_page_url).read())
    firsttime = True
    nexturl = nextPageExist(soup)
    results=[]
    ALL_URLs=[]
    while firsttime or nexturl is not None:
        Page_URLs = soup.find_all("a",attrs={"class": "smallV110"})#only one result normally
        for u in Page_URLs:
            ALL_URLs.append("http://apps.webofknowledge.com"+u['href'])
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
    for url in ALL_URLs:
        results.append(get_pmid_doi_title_numCitaions(url))
    return results

def get_all_citations(reURL):
    soup = BeautifulSoup(urllib2.urlopen(reURL).read())
    URL = soup.find("a",attrs={"class": "smallV110"})#only one result normally
    if URL is not None:
        url = "http://apps.webofknowledge.com"+URL['href']
        soup_citaions = BeautifulSoup(urllib2.urlopen(url).read())
        citations_link = soup_citaions.find("a",attrs={"title": "View all of the articles that cite this one"})
        if citations_link is not None:
            return get_citations_doi_pmid("http://apps.webofknowledge.com" + citations_link['href'])
    return None


def citationNetwork(pmidList, titleList, doiList):
    for (pmid,title,doi) in zip(pmidList, titleList, doiList):
        if doi:
            reURL = _getResultURL(1,doi)
        elif title:
            reURL = _getResultURL(2,title)
        else:
            print >> sys.stderr , "Cannot find the data of PMID =",pmid
        if reURL is not None:
            get_all_citations(pmid,reURL)

def citations_for_pmid(pmid,title,doi):
    if doi:
        reURL = _getResultURL(1,doi)
    elif title:
#         return { pmid: None}
        reURL = _getResultURL(2,title)
    else:
        print >> sys.stderr , "Cannot find the data of PMID =",pmid
    if reURL is not None:
        result ={ pmid: get_all_citations(reURL)}
        pickle.dump(result, open(citations_path+pmid+'.pkl','wb'))
        print pmid
        sys.stdout.flush()
    

def remove_None(seq):
    return [x for x in seq if x is not None]

def get_pmid_doi_title_numCitaions(url):
    content=urllib2.urlopen(url).read()
    return get_tag(content,'doi'), get_tag(content,'pmid'), get_tag(content,'title'), get_tag(content,'numCitations')

def get_tag(content,tag):
    soup = BeautifulSoup(content)
    if tag=='title':
        try:
            return soup.find('div',attrs={"class": "title"}).get_text().strip()
        except:
            pass
    content=soup.find_all('p',attrs={"class": "FR_field"})
    for field in content:
        if field.find("span"):
            if field.find("span").get_text().strip()=={'doi':'DOI:','pmid':'PubMed ID:','numCitations':'Times Cited in Web of Science Core Collection:'}[tag]:
                if field.find("value"):
                    return field.find("value").get_text().strip()
                elif tag == 'numCitations':
                    return field.find("b").get_text().strip()
    return None

def citations_for_pmid_helper(param):
    try:
        citations_for_pmid(**param)
    except:
        pass

def save_citations(num_threads=20):
    fileout=path+'Datasets/citations.pkl'
    try:
        pmid_processed_sofar= map(str.strip,open(fileout.replace('.pkl','.log')).readlines())
    except:
        pmid_processed_sofar=[]
    pmidList= MEDLINEServer.MEDLINEServer.loadPMIDs(path)
    
    PT=pickle.load(open(path+'Datasets/PT.pkl'))
    PDOI=pickle.load(open(path+'Datasets/PDOI.pkl'))
    params=[{'pmid':pmid, 'doi':PDOI[pmid],'title':PT[pmid]} for pmid in pmidList if pmid not in pmid_processed_sofar]
    print '\nTotal PMID: {}\nProcessed So far: {}\nRemaining: {}\nNum_Threads: {}'.format(len(pmidList), len(pmid_processed_sofar), len(params), num_threads)
    old_stdout = sys.stdout
    if not os.path.exists(path+'Log'):            os.makedirs(path+'Log')
    sys.stdout = open(path+'Log/citations.pkl','a')
    sys.stderr = open(path+'Log/citations.pkl','w')
    if num_threads==1:
        for p in params:    citations_for_pmid_helper(p)
    else:
        multiprocessing.Pool(num_threads).map(citations_for_pmid_helper,params)
    sys.stdout = old_stdout

def getLen(item):
    if item:
        return len(item)
    return 0

def merge_saved_pickle_files():
    files = [ citations_path+f for f in os.listdir(citations_path) if os.path.isfile(os.path.join(citations_path,f)) ]
    results={}
    for f in files:
        results.update(pickle.load(open(f,'rb')))
    fileout=path+'Datasets/{}.pkl'.format('citations')
    pickle.dump(results, open(fileout,'wb'))
    print 'Merging {} citation files is done at {}!'.format(len(files),fileout)

if __name__ == '__main__':
    save_citations(num_threads=15)
#     merge_saved_pickle_files()
    
        

