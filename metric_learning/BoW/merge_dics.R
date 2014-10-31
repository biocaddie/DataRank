rm(list=ls())
path='/home/arya/workspace//biocaddie/metric_learning/MeSH.dic/'
dic1=read.table(paste(path,"mesh1.dic",sep=""))
dic2=read.table(paste(path,"mesh2.dic",sep=""))
dic=union(dic1[,1],dic2[,1])
write.table(dic,paste(path,"mesh.dic",sep=""))
