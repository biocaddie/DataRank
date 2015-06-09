    def MEDLINEparser4AbsTlMh(self,doc,docDir):
        """parse medline plain text for abstracts and titles"""
        fin=file(os.path.join(docDir,doc))#.read().split("\n")
        recs = fin.readlines()
        newEntry=False
        firstLine = True
        newLine = True
        
        textList = []
        textDict = {}
        for line in recs:
            if line.startswith("PMID-"):
                pmid = line.split("- ")[1].strip("\n") #\n\r
                newEntry=True
                firstLine = False
                newLine = True
                textList = []
                
            if newEntry and line.startswith("AB  - "):
                absRaw = line.split("AB  - ")[1].strip("\n") # \n\r
                textList.append(absRaw.strip(" "))
                newLine = False
        
            if newEntry and line.startswith("TI  - "):
                ttRaw = line.split("TI  - ")[1].strip("\n")
                textList.append(ttRaw)
                newLine = False
            
            if newEntry and line.startswith("MH  - "):
                meshRaw = line.split("MH  - ")[1].strip("\n") # \n\r
                mesh = meshRaw.split("/")[0].strip("*")
                textList.append(mesh)            
            
            if line.startswith(" ") and (not newLine):
                textList.append(line.strip("\n").strip(" "))
        
            if not line.startswith("AB") and not line.startswith("TI") and not line.startswith(" "):
                newLine = True
        
            if (not firstLine) and line=="\n":
                textDict[pmid] = textList
                newEntry=False
                
        for k in textDict.keys():
            textDict[k] = " ".join(textDict[k])
        return textDict