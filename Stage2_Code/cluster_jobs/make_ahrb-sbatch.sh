#!/bin/bash

subj_ids=$1
ses=1
sample=ahrb

if [ -z "$1" ]; then
	echo
	echo "Error: Missing list. Provide subject list w/o 'sub-' prefix in positon 1."
	echo
	exit 1
fi

n=0
cat $subj_ids | while read line ; do

	sed -e "s|SUBJECT|${line}|g; s|SESSION|${ses}|g" ./templates/${sample}_firstlvl.txt > ./batch_${sample}/first${n}
	n=$((n+1))

done

chmod +x ./batch_${sample}/first*

