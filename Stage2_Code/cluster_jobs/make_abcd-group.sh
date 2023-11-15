#!/bin/bash

curr_dir=`pwd`
sample=abcd # abcd, ahrb or mls
task=MID
ses=baselineYear1Arm1 # baselineYear1Arm1 or 2YearFollowUpArm1 for ABCD
type=run # run or session
subj_list=${curr_dir}/subj_ids/abcd_ids.txt
inpfold=/scratch.global/${USER}/analyses_reliability/firstlvl
outfold=/scratch.global/${USER}/analyses_reliability/group


# Model permutations
if [[ $sample == 'abcd' || $sample == 'ahrb' ]]; then
    fwhm_opt=(3.6 4.8 6.0 7.2 8.4)
elif [[ $sample == 'mls' ]]; then
    fwhm_opt=(3.6 4.8 6.0 7.2 8.4)
fi

motion_opt=("opt1" "opt2" "opt3" "opt4" "opt5")
modtype_opt=("CueMod" "AntMod" "FixMod")

# Start loop to create ICC batch jobs
n=0
for fwhm in ${fwhm_opt[@]} ; do
	for motion in ${motion_opt[@]} ; do
		for modtype in ${modtype_opt[@]} ; do
			model="mask-mni152_mot-${motion}_mod-${modtype}_fwhm-${fwhm}"
			sed -e "s|MODEL|${model}|g; s|SESSION|${ses}|g; s|TASK|${task}|g; s|TYPE|${type}|g;  s|INPUT|${inpfold}|g; s|OUTPUT|${outfold}|g; s|SUBJ_IDS|${subj_list}|g; s|SAMPLE|${sample}|g;" ./templates/group.txt > ./batch_jobs/group${n}
        		n=$((n+1))
	        done
    	done
done

chmod +x ./batch_jobs/group*
