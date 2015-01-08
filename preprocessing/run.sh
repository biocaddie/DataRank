python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/parsed.5000.db  -p parse
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/parsed.db  -p parse
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/testclean.db  -p parse-clean

python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/cleanest.db  -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/clean_withNum.db -R clean_withNum  -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/clean_noStemming.db -R clean_noStemming  -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/clean_withNum_noSteming.db -R clean_withNum_noSteming  -p parse-clean &
python preprocess.py -src /home/arya/storage/raw.db -dst /home/arya/storage/test.db  -R test -p parse-clean
python preprocess.py -src /home/arya/storage/test.db    -p  tfidf &

python preprocess.py -src /home/arya/storage/test.db -dst /home/arya/storage/test0.02.db  -p reduce -th 0.02 &
python preprocess.py -src /home/arya/storage/cleanest.db -p reduce -th 0.2



python preprocess.py -src /home/arya/parsed.5000.db -dst /home/arya/clean.5000.db  -p clean


-src /home/arya/storage/test.db -p convertlda 
