#!/bin/bash

subj_ids=$1
ses=baselineYear1Arm1
out_dir=/scratch.global/${USER}/analyses_reliability

if [ -z "$1" ]; then
	echo
	echo "Error: Missing list. Provide subject list w/o 'sub-' prefix in positon 1."
	echo
	exit 1
fi

n=0
cat $subj_ids | while read line ; do

	sed -e "s|SUBJECT|${line}|g; s|SESSION|${ses}|g; s|OUTPUT|${out_dir}|g;" ./templates/abcd_firstlvl.txt > ./batch_jobs/first${n}
	n=$((n+1))

done

chmod +x ./batch_jobs/first*

