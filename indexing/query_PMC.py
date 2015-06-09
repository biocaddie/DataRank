    def getFullTextXML(self,pmcIdList,xmlDir):
        """retrieve PMC full text in xml format; query is a list of PMC ID"""
        retstart = 0
        step = 1000
        i=0
        ite = len(pmcIdList)/step*1.0
        print "Retrieve all KD full text from PMC in %f iterations." %ite
        while i<=ite:
            query = pmcIdList[retstart:retstart+step]
            handle=Entrez.efetch(db="pmc",id=query,retmode="xml")
            record=handle.read()
            handle.close()
            # output
            fout=file(os.path.join(xmlDir,"Kawasaki_PMC_fulltext_batch%d.xml"%i),"w")
            fout.write(record)
            # update index
            retstart += step
            i+=1  