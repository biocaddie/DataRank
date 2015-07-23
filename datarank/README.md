DataRank Search Engine
=========
In this project we're creating a search engine for for biomedical datasets. The idea is to create a recommender system behind the search engine to make searches and recommendations more efficient. Roughly speaking, this priject involves several nontrivial tasks:
 a (offline) recommender system has several component:

**1- Requirements:** 'postgresql', 'django', 'psycopg2' should be installed. 
'''
sudo apt-get install postgresql postgresql-contrib
sudo pip install Django
sudo pip install psycopg2
sudo pip install django-ipware
''''

**2- Database:**

sudo -u postgres psql -c "CREATE USER arya WITH SUPERUSER CREATEDB CREATEROLE PASSWORD 'arya';"

sudo -u postgres createdb datarank

python manage.py syncdb

 
ln -s /home/arya/PubMed/GEO/Datasets/wordcloud /home/arya/workspace/biocaddie/datarank/search/static/wordcloud 

**3- Run:** 
python manage.py runserver 0.0.0.0:8888
