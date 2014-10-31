rm(list=ls())
library(XML)
library(tm)
library(NLP)
name='/home/arya/datasets/ap/ap2.xml'
data=xmlParse(name)
# xml_data <- xmlToList(data)
d<-xmlToDataFrame(data)
row.names(d)<-d[,1]
d$DOCNO<-NULL
corpus<-VCorpus(DataframeSource(d))
preprocessing=TRUE
M1<-DocumentTermMatrix(corpus, control = list(removePunctuation = FALSE,
                                             stopwords = FALSE,
                                             removeNumbers=FALSE,
                                             stemDocument=FALSE,
                                             removeWords=FALSE,
                                             stripWhitespace=FALSE,
                                             wordLengths = c(1, Inf)));
T1<-as.data.frame(Terms(M1))
if(preprocessing)
{
  print("Lower Casing...")
  corpus <- tm_map(corpus, content_transformer(tolower))
  print("Removing Punctuation...")
  corpus <- tm_map(corpus, removePunctuation)
  print("Removing Striping Whitespace...")
  corpus <- tm_map(corpus, stripWhitespace)
  print("Removing Numbers...")
  corpus <- tm_map(corpus, removeNumbers)
  print("Removing Stop Words...")
  corpus <- tm_map(corpus, content_transformer(removeWords), stopwords("english"))
  corpus <- tm_map(corpus, content_transformer(removeWords), stopwords("SMART"))
  print("Stemming...")
  corpus<-tm_map(corpus, stemDocument)
}
M2<-DocumentTermMatrix(corpus, control = list(removePunctuation = FALSE,
                                             stopwords = FALSE,
                                             removeNumbers=FALSE,
                                             stemDocument=FALSE,
                                             removeWords=FALSE,
                                             stripWhitespace=FALSE,
                                             wordLengths = c(1, Inf)));
T2<-as.data.frame(Terms(M2))

M3 <- DocumentTermMatrix(corpus, control = list(weighting = function(x) weightTfIdf(x, normalize =FALSE),
                                               removePunctuation = FALSE,
                                               stopwords = FALSE,
                                               removeNumbers=FALSE,
                                               stemDocument=FALSE,
                                               removeWords=FALSE,
                                               stripWhitespace=FALSE,
                                               wordLengths = c(1, Inf)))
T3<-as.data.frame(Terms(M3))

M4 <- DocumentTermMatrix(corpus, control = list(weighting = function(x) weightTfIdf(x, normalize =TRUE),
                                                removePunctuation = FALSE,
                                                stopwords = FALSE,
                                                removeNumbers=FALSE,
                                                stemDocument=FALSE,
                                                removeWords=FALSE,
                                                stripWhitespace=FALSE,
                                                wordLengths = c(1, Inf)))
sink('NUL') #supress output
tfidf<-colSums(inspect( M4))
sink() #undo  suppression
T5<-as.data.frame(tfidf[tfidf>0.15685])

dic<-as.data.frame(row.names(T5))
dic_blei=read.table('/home/arya/datasets/ap/vocab.txt')

dic_blei_sort<-as.data.frame(sort(dic_blei[,1]))

dic_union<-union(dic[,1], dic_blei[,1])
dic_intersect<-intersect(dic[,1], dic_blei[,1])
dic_diff<-setdiff(dic_union,dic_intersect)
write.table(dic,'/home/arya/datasets/ap/vocab.arya', quote=FALSE, row.names = FALSE, col.names = FALSE)
write.table(dic_union,'/home/arya/datasets/ap/vocab.union',quote=FALSE, row.names = FALSE, col.names = FALSE)
write.table(dic_diff,'/home/arya/datasets/ap/vocab.symdiff',quote=FALSE, row.names = FALSE, col.names = FALSE)
names(dic)<-c('words')
nTerms(M4)
M5<-M2[,unlist(lapply(dic$words, as.character))]
inspect(M5[1:10,1:100])

M6<-dtm2ldaformat(M5)
vv<-M6$vocab
dd<-M6$documents
dd[1]
C<-NULL
C$i<-M5$i
C$j<-M5$j
C$v<-M5$v
C<-as.data.frame(C)
m <- inspect(M5)
DF <- as.data.frame(m, stringsAsFactors = FALSE)
write.table(DF, '/home/arya/datasets/ap/ap.arya')
