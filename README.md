bioCADDIE
=========
In this project we're creating a search engine for for biomedical datasets. The idea is to create a recommender system behind the search engine to make searches and recommendations more efficient. Roughly speaking, this priject involves several nontrivial tasks:
 a (offline) recommender system has several component:

**1- Indexing:** In this part we create a corpus, a bipartite paper-dataset graph which shows which paper has cited which datasets, for machine learning. This involves mining full text papers for direct and indirect references to datasets.  

**2- Metric Learning:** learning a similarity metric for datasets and papers: we can have this similarity measure more meaningfully and abstractly if we knew the topics of paper and dataset. Using topic models we can have a mixed-membership model, (each paper or dataset has all the topics but with different probabilities). Having this topics, we can find the latent (graph) structure  between topics using Mesh and UMLS. Having this graph and topics we can easily compute the similarity between papers and between topics and between topic and papers.

**3- Recommender System:** Using user's click data and this similarity metric, we can perform user-based (Netflix), item-based (Amazon), content-based (google search),  Context-based (google-ads) recommendations

**4-Search Engine:** We can now create search engine by creating an inverted index between key-words and datasets and learning-to-rank techniques.
