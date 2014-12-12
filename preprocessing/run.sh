python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/cleanest.db  -D 1 -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/clean_withNum.db -R clean_withNum  -D 1 -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/clean_noStemming.db -R clean_noStemming  -D 1 -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/clean_withNum_noSteming.db -R clean_withNum_noSteming  -D 1 -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/test.db  -D 1 -R test -p parse-clean
python preprocess.py -src /home/arya/storage/test.db    -D 1 -p  tfidf &

python preprocess.py -src /home/arya/storage/test.db -dst /home/arya/storage/test0.02.db  -D 1 -p reduce -th 0.02 &
python preprocess.py -src /home/arya/storage/cleanest.db -dst /home/arya/storage/cleanest002.db  -D 1 -p reduce -R reduce0.02 -th 0.02

-src /home/arya/storage/test.db -p convertlda 
