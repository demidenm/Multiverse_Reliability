#!/bin/bash

curr_dir=`pwd`
sample=abcd # abcd, ahrb or mls
task=MID
run=2 # 1, 2 or None (no need for leading 0, added in code
ses=2YearFollowUpYArm1 # baselineYear1Arm1 or 2YearFollowUpYArm1 for ABCD
type=run # run or session
subj_list=${1}
outfold=/scratch.global/${USER}/analyses_reliability/group_lowmotion
counter_start=300 #0, 60, 120, 180, 240, 300 to run run-1 & run-2 & session in batch across both sesions

if [ -z "$1" ]; then
        echo
	echo "Error: Missing list. Provide subject list w 'sub-' prefix in positon 1."
        echo
	exit 1
fi

# if using runs, inp should be firstlvl; if using sessions, inp should be fixedeff
if [ ${type} == 'session' ]; then
	inpfold=/scratch.global/${USER}/analyses_reliability/fixedeff
elif [ ${type} == 'run' ]; then
	inpfold=/scratch.global/${USER}/analyses_reliability/firstlvl
else
                echo "Invalid type: $type"
fi

# Model permutations
if [[ $sample == 'abcd' || $sample == 'ahrb' ]]; then
    fwhm_opt=(3.6 4.8 6.0 7.2 8.4)
elif [[ $sample == 'mls' ]]; then
    fwhm_opt=(3.0 4.0 5.0 6.0 7.0)
fi

motion_opt=("opt1" "opt2" "opt3" "opt4") # "opt5" "opt6")
modtype_opt=("CueMod" "AntMod" "FixMod")

# Start loop to create ICC batch jobs
n=${counter_start}
for fwhm in ${fwhm_opt[@]} ; do
	for motion in ${motion_opt[@]} ; do
		for modtype in ${modtype_opt[@]} ; do
			model="mask-mni152_mot-${motion}_mod-${modtype}_fwhm-${fwhm}"
			sed -e "s|MODEL|${model}|g; s|RUN|${run}|g; s|SESSION|${ses}|g; s|TASK|${task}|g; s|TYPE|${type}|g;  s|INPUT|${inpfold}|g; s|OUTPUT|${outfold}|g; s|SUBJ_IDS|${subj_list}|g; s|SAMPLE|${sample}|g;" ./templates/group.txt > ./batch_jobs/group${n}
        		n=$((n+1))
	        done
    	done
done

chmod +x ./batch_jobs/group*
