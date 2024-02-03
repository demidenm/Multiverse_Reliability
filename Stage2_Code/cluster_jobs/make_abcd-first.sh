#!/bin/bash

subj_ids=$1
acomp_list=$1 # tsv file, no header, col1 = sub IDs w/ sub- prefix and col2 acompcor exclusion "1" non-exclusion "0"
ses=baselineYear1Arm1
out_dir=/scratch.global/${USER}/analyses_reliability

if [ -z "$1" ]; then
	echo
	echo "Error: Missing list. Provide subject list w 'sub-' prefix in positon 1."
	echo
	exit 1
fi

n=0
cat $subj_ids | while read line ; do
	subj=$(echo $line | awk -F" " '{ print $1 }' | awk -F"-" '{ print $2 }')
	sed -e "s|SUBJECT|${subj}|g; s|SESSION|${ses}|g; s|OUTPUT|${out_dir}|g; s|ACOMPCOR|${acomp_list}|g;" ./templates/abcd_firstlvl.txt > ./batch_jobs/first${n}
	n=$((n+1))

done

chmod +x ./batch_jobs/first*

