class Node:
    """Node of the MeSH Tree"""
    def __init__(self,meshID,term):
        self.meshID=meshID
        self.term=term
        self.parents=[ ]
        self.children=[ ]

def build_data(filepath):
    """Gets parents and children of each node and returns a meshID --> Node dictionary"""
    data=open(filepath,'r')
    meshID_to_Node={}
    pathID_to_Node={}

    for line in data.readlines():
        meshID,term,pathID=line.split('|')
        pathID=pathID.strip()
        try:
            meshID_to_Node[meshID]
        except KeyError:
            meshID_to_Node[meshID]=Node(meshID,term)

        pathID_to_Node[pathID]=meshID_to_Node[meshID]

    for pathid,node in pathID_to_Node.iteritems():
        parent=pathid.rsplit('.',1)
        if len(parent)!=2:
            continue
        try:
            n=pathID_to_Node[parent[0]]
            n.children.append(node.meshID)
            node.parents.append(n.meshID)
        except KeyError:
            continue
    return meshID_to_Node
