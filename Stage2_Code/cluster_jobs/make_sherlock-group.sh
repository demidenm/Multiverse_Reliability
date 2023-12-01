#!/bin/bash

curr_dir=`pwd`
sample=AHRB # abcd, AHRB, MLS
task=mid # mid = AHRB, reward = MLS
ses=1 # 1 or 2
type=ses # run or ses
subj_list=$1 
inpfold=/oak/stanford/groups/russpold/data/${sample}/derivatives/analyses/proj_reliability/fixedeff
outfold=/oak/stanford/groups/russpold/data/${sample}/derivatives/analyses/proj_reliability/group


# Model permutations
if [[ $sample == 'abcd' || $sample == 'AHRB' ]]; then
    fwhm_opt=(3.6 4.8 6.0 7.2 8.4)
elif [[ $sample == 'MLS' ]]; then
    fwhm_opt=(3.0 4.0 5.0 6.0 7.0)
fi

motion_opt=("opt1" "opt2" "opt3" "opt4" "opt5")
modtype_opt=("CueMod" "AntMod" "FixMod")

# Start loop to create ICC batch jobs
n=0
for fwhm in ${fwhm_opt[@]} ; do
	for motion in ${motion_opt[@]} ; do
		for modtype in ${modtype_opt[@]} ; do
			model="mask-mni152_mot-${motion}_mod-${modtype}_fwhm-${fwhm}"
			sed -e "s|MODEL|${model}|g; s|SESSION|${ses}|g; s|TASK|${task}|g; s|TYPE|${type}|g;  s|INPUT|${inpfold}|g; s|OUTPUT|${outfold}|g; s|SUBJ_IDS|${subj_list}|g; s|SAMPLE|${sample}|g;" ./templates/group_sherlock.txt > ./batch_jobs/group${n}
        		n=$((n+1))
	        done
    	done
done

chmod +x ./batch_jobs/group*

echo
echo "Files created. Make sure the group .py script has the correct beta/effect and session/run abbreviations"
echo
