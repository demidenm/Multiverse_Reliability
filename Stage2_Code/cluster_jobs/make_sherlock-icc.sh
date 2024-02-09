#!/bin/bash

sample=AHRB # abcd, AHRB, MLS
task=mid # mid = AHRB, reward = MLS
ses=1 # 1 or 2
mask_label=None # None, or wilson-sub, wilson-supra
type=run # run or session
outfold=/oak/stanford/groups/russpold/data/${sample}/derivatives/analyses/proj_reliability/icc_mods
scratch=/scratch/groups/russpold/${USER}/${sample}

# if using runs, inp should be firstlvl; if using sessions, inp should be fixedeff
if [ ${type} == 'session' ]; then
	inpfold=/oak/stanford/groups/russpold/data/${sample}/derivatives/analyses/proj_reliability/fixedeff
elif [ ${type} == 'run' ]; then
	inpfold=/oak/stanford/groups/russpold/data/${sample}/derivatives/analyses/proj_reliability/firstlvl
else
         	echo "Invalid type: $type"
fi

# Model permutations
if [[ $sample == 'abcd' || $sample == 'AHRB' ]]; then
    fwhm_opt=(3.6 4.8 6.0 7.2 8.4)
elif [[ $sample == 'MLS' ]]; then
    fwhm_opt=(3.0 4.0 5.0 6.0 7.0)
fi

motion_opt=("opt1" "opt2" "opt3" "opt4") # "opt5" + "opt6" are opt3/opt4 w/ mFD < .9
modtype_opt=("CueMod" "AntMod" "FixMod")

contrasts=(
    'Lgain-Neut' 'Sgain-Neut'
    'Lgain-Base' 'Sgain-Base'
)


# Start loop to create ICC batch jobs
n=0
for con in ${contrasts[@]} ; do
    for fwhm in ${fwhm_opt[@]} ; do
        for motion in ${motion_opt[@]} ; do
            for modtype in ${modtype_opt[@]} ; do
                model="contrast-${con}_mask-mni152_mot-${motion}_mod-${modtype}_fwhm-${fwhm}"
		sed -e "s|MODEL|${model}|g; s|TASK|${task}|g; s|SAMPLE|${sample}|g; s|SESSION|${ses}|g; s|MASKLABEL|${mask_label}|g; s|TYPE|${type}|g;  s|INPFOLD|${inpfold}|g; s|OUTFOLD|${outfold}|g; s|SCRATCH|${scratch}|g;" ./templates/icc_sherlock.txt > ./batch_jobs/icc${n}
        	n=$((n+1))
            done
        done
    done
done

#!/bin/bash

chmod +x ./batch_jobs/icc*
