def getFeatures(line):
    features = line.split(';')
    ID = features[0]
    MeSH = ';'.join(features[1:-1])
    Count = features[-1]
    return (ID, MeSH, Count)

with open('search/data/dataset_top_mesh_citation.txt', 'r') as f:
    data = f.read().split('\n')[:-1]
    InfoTuple = map(getFeatures, data)
    # print len(InfoTuple)


from search.models import Dataset

def saveData(info):
    q = Dataset()
    q.ID = info[0]
    q.Features = info[1]
    q.Count = info[2]
    q.save()

map(saveData, InfoTuple)
