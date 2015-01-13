python preprocess.py -src /home/arya/storage/parsed.db -tfidf  -stm 0 -p clean

python preprocess.py -src /home/arya/storage/parsed.db -tfidf -thtf 10  -stm 1 -p clean
python preprocess.py -src /home/arya/storage/parsed.db -tfidf -thtf 10  -stm 0 -p clean


python preprocess.py -src /home/arya/storage/parsed.db -tfidf -thtf 50  -stm 1 -p clean
python preprocess.py -src /home/arya/storage/parsed.db -tfidf -thtf 50  -stm 0 -p clean

