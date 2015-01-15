#!/bin/bash

for i in {0..1710}
do
        A="python article_mesh.py -s PubMed/MEDLINE/Medline_batch"
        C=".xml -d mesh.db -t article_mesh"
        run=$A$i$C
        $run
    echo batch $i done
done
