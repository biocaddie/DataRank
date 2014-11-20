python preprocess.py -src /home/public/raw.db -dst /home/public/parsed.db  -D1 -p parse &

python preprocess.py -src /home/public/hctest.db -dst /home/public/abstracts_clean.db  -D 1 -p parse-clean &

python preprocess.py -src /home/public/abstracts_clean.db -D 1 -p tfidf -th 0.03 &

preprocess.py -src /home/arya/abstracts_clean.db -D 1  -p reduce -th 0.03 &
