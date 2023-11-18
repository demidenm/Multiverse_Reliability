#!/bin/bash

subj_ids=$1
ses=1
sample=AHRB
task=mid
inp_path=/oak/stanford/groups/russpold/data/${sample}

if [ -z "$1" ]; then
	echo
	echo "Error: Missing list. Provide subject list w/o 'sub-' prefix in positon 1."
	echo
	exit 1
fi

n=0
cat $subj_ids | while read line ; do

	sed -e "s|SUBJECT|${line}|g; s|SESSION|${ses}|g; s|TASK|${task}|g; s|DATA_LOC|${inp_path}|g; s|SAMPLE|${sample}|g;" ./templates/${sample,,}_firstlvl.txt > ./batch_jobs/first${n}
	n=$((n+1))

done

chmod +x ./batch_jobs/first*

