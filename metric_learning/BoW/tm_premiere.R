rm(list=ls())
library(tm)
library(plyr)
x<-c("aba 111 2 3 4 Hello. hello! I am Arya",
     "Hello? HellO HeLLO?!? my name is Arya1 12 63 iran-mehr not only make makes",
     "running runner runs ARYA",
     "happyness happies AryA");corpus <- Corpus(VectorSource(x));

M1<-DocumentTermMatrix(corpus, control = list(removePunctuation = FALSE,
                                              stopwords = FALSE,
                                              removeNumbers=FALSE,
                                              stemDocument=FALSE,
                                              removeWords=FALSE,
                                              stripWhitespace=FALSE,
                                              wordLengths = c(1, Inf)));
T1<-as.data.frame(Terms(M1))
inspect(M1)

corpus <- tm_map(corpus, content_transformer(tolower))
corpus <- tm_map(corpus, removePunctuation)
corpus <- tm_map(corpus, stripWhitespace)
corpus <- tm_map(corpus, removeNumbers)
corpus <- tm_map(corpus, content_transformer(removeWords), stopwords("english"))
corpus <- tm_map(corpus, content_transformer(removeWords), stopwords("SMART"))
corpus<-tm_map(corpus, stemDocument)

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

M4 <- DocumentTermMatrix(corpus, control = list(weighting = function(x) weightTfIdf(x, normalize =TRUE),
                                                removePunctuation = FALSE,
                                                stopwords = FALSE,
                                                removeNumbers=FALSE,
                                                stemDocument=FALSE,
                                                removeWords=FALSE,
                                                stripWhitespace=FALSE,
                                                wordLengths = c(1, Inf)))
T3<-as.data.frame(Terms(M3))
inspect(corpus)
inspect(M2)
inspect(M3)
inspect(M4)

findFreqTerms(M4, 0.7, 1)
termFreq(M4)

weightTfIdf(M3,normalize = TRUE)
Te(M4)



a<-as.data.frame(inspect(M4))

sink('NUL') #supress output
tfidf<-colSums(inspect( M4))
sink() #undo  suppression
tfidf[tfidf>0.5]


# getTransformations()
# (f <- content_transformer(function(x, pattern) gsub(pattern, "", x)))
# corpus<-tm_map(corpus, f, "[[:digit:]]+")[[1]]
# a<-rowSums(inspect( M5[ , dimnames(M5)$Docs] ))