#!/bin/bash

sample=abcd # abcd, ahrb or mls
ses=baselineYear1Arm1 # baselineYear1Arm1 or 2YearFollowUpArm1 for ABCD
mask_label=None # None, wilson-sub, wilson-supra
type=run # run or session
subj_ids=${1} # sub-IDs, move to temp to differentiate low/high motion mods

# if using runs, inp should be firstlvl; if using sessions, inp should be fixedeff
if [ ${type} == 'session' ]; then
	inpfold=/scratch.local/${USER}/analyses_reliability/fixedeff
		
elif [ ${type} == 'run' ]; then
	inpfold=/scratch.local/${USER}/analyses_reliability/firstlvl

else
         	echo "Invalid type: $type"
fi

# Contrasts
contrasts=(
    'Lgain-Neut' 'Sgain-Neut'
    'Lgain-Base' 'Sgain-Base'
)

# Model permutations
if [[ $sample == 'abcd' || $sample == 'ahrb' ]]; then
    fwhm_opt=(3.6 4.8 6.0 7.2 8.4)
elif [[ $sample == 'mls' ]]; then
    fwhm_opt=(3.6 4.8 6.0 7.2 8.4)
fi

motion_opt=("opt1" "opt2" "opt3" "opt4") # "opt5" "opt6")
modtype_opt=("CueMod" "AntMod" "FixMod")

# Start loop to create ICC batch jobs
n=0
for con in ${contrasts[@]} ; do
    for fwhm in ${fwhm_opt[@]} ; do
        for motion in ${motion_opt[@]} ; do
            for modtype in ${modtype_opt[@]} ; do
                model="contrast-${con}_mask-mni152_mot-${motion}_mod-${modtype}_fwhm-${fwhm}"
		sed -e "s|MODEL|${model}|g; s|SUBJ_IDS|${subj_ids}|g; s|SESSION|${ses}|g; s|MASKLABEL|${mask_label}|g; s|TYPE|${type}|g;  s|INPFOLD|${inpfold}|g" ./templates/abcd_icc.txt > ./batch_jobs/icc${n}
        	n=$((n+1))
            done
        done
    done
done

#!/bin/bash

chmod +x ./batch_jobs/icc*
