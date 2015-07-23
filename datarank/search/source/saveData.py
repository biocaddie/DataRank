from search.models import Dataset
def save(row):
    d = Dataset()
    d.ID = row.accession
    d.Url = "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=" + row.accession
    d.PMID= row.pmid
    d.Summary= row.summary
    d.Title= row.accession+': '+row.title
    d.Features = ';'.join(row.mesh)
    d.Count = row.cpcc
    d.save()

def saveAll():
    import pandas as pd
    d=pd.read_pickle('/home/arya/PubMed/GEO/Datasets/D.Web.df')
    d.apply(save,axis=1)

