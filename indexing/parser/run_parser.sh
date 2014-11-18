#!/bin/bash

for i in {0..1761}
do
	A="python parser.py patternList  /home/public/PubMed/PMC_XML/PMC_batch"
	C=".xml  /home/public/parsed.db"
	run=$A$i$C
	$run
	echo batch $i done
done