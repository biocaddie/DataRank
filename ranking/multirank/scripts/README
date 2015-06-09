1. query_ncbi_2.py
    queries ncbi for medline, cited by
    params to change: degree and b_cancer dictionary

2. parse_medline.py
    parses medline extracts.
    params to change: author cut off, top journals, input/output files

3. multi_load_dicts.py
    loads the dictionaries from parse_medline
    called from corank and multirank
    also use this to sanity check results

4. corank.py
    
5. multirank.py
    uses dictionaries from (3) and creates the matlab data to load sparse tensor

6. multi.m (or demo.m + data.mat for original)
    runs multirank. Need to pass the output from multirank.py (load_A.m)

7. display_results.m
    just sorts and prints out top ranked values from multi.m 


One of the python files (commented out or might be in old/test folder) has the journal/dataset counts to make the linear weighting. But easy to rewrite once dictionaries are loaded.


