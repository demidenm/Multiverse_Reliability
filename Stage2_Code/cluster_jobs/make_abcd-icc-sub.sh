#!/bin/bash

ses=baselineYear1Arm1 # baselineYear1Arm1 or 2YearFollowUpArm1 for ABCD
task=MID
model=contrast-Sgain-Base_mask-mni152_mot-opt1_mod-CueMod_fwhm-8.4
min=25
max=525
subj_ids=${1} # sub-IDs, to subsample from to create set1 and set2 for ICC
seed_list=${2} # list of 100 seeds for subsampling
inpfold=/scratch.global/${USER}/analyses_reliability/firstlvl
outfold=/scratch.global/${USER}/analyses_reliability/subsample/icc_subsample/ses-${ses}

n=0
cat ${seed_list} | while read line ; do
	sed -e "s|MODEL|${model}|g; \
		s|SUBJ_IDS|${subj_ids}|g; \
		s|SEED|${line}|g; \
		s|TASK|${task}|g; \
		s|SESSION|${ses}|g; \
		s|MIN_N|${min}|g; \
		s|MAX_N|${max}|g; \
		s|INPFOLD|${inpfold}|g; \
		s|OUTFOLD|${outfold}|g" ./templates/abcd_icc-subsample.txt > ./batch_jobs/icc${n}
	n=$((n+1))
done


chmod +x ./batch_jobs/icc*
