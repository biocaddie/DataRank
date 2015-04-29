from search.models import Dataset

prefix_gse = "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc="
prefix_genbank = "http://www.ncbi.nlm.nih.gov/nuccore/"
def addURL(data):
    if data.ID.startswith('GSE'):
        data.Url = prefix_gse+data.ID
    else:
        data.Url = prefix_genbank+data.ID
    # print data.Url
    data.save()

datas = Dataset.objects.all()
map(addURL, datas)