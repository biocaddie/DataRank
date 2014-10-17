rm(list=ls())
library(XML)
library(plyr)
library(tm)
name='/home/arya/datasets/ap/ap.xml'
data=xmlParse(name)
xml_data <- xmlToList(data)
d<-xmlToDataFrame(data)
row.names(d)<-d[,1]
d$DOCNO<-NULL
a<-VCorpus(DataframeSource(d))
adtm <-DocumentTermMatrix(a) 

summary(a)  #check what went in
a <- tm_map(a, removeNumbers)
a <- tm_map(a, removePunctuation)
a <- tm_map(a , stripWhitespace)
a <- tm_map(a, tolower)
a <- tm_map(a, removeWords, stopwords("english")) # this stopword file is at C:\Users\[username]\Documents\R\win-library\2.13\tm\stopwords 
a <- tm_map(a, stemDocument, language = "english")
adtm <-DocumentTermMatrix(a) 
