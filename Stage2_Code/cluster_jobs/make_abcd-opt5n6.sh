#!/bin/bash

# Description:
# This script makes copies of files generated from pipelines with opt3 and 4 for 
#  subjects that have a mean framewise-displacement <0.9. The subject list that is included should contain sub-IDs with mFD<.9 
# This is done to avoid rerunning high resource modeling.

# Set meaningful variable names
subject_list="${1}"
first_level_input="/scratch.global/${USER}/analyses_reliability/firstlvl"
fixed_effect_input="/scratch.global/${USER}/analyses_reliability/fixedeff"
session="baselineYear1Arm1"

# Loop through each subject in the list
cat "${subject_list}" | while read sub ; do
    
# Process first-level input
	for file in "${first_level_input}/ses-${session}/${sub}"/*_mot-opt3_*; do
	    		dir=$(dirname "${file}")
	    		filename=$(basename "${file}")
	    		new_filename="${filename//_mot-opt3_/_mot-opt5_}"
	    		cp "${file}" "${dir}/${new_filename}" || echo "Failed to copy ${file}"
	done

	for file in "${first_level_input}/ses-${session}/${sub}"/*_mot-opt4_*; do
		dir=$(dirname "${file}")
		filename=$(basename "${file}")
		new_filename="${filename//_mot-opt4_/_mot-opt6_}"
		cp "${file}" "${dir}/${new_filename}" || echo "Failed to copy ${file}"
	done

	# Process fixed effect input (similar to first-level input)
	for file in "${fixed_effect_input}/ses-${session}/${sub}"/*_mot-opt3_*; do
		dir=$(dirname "${file}")
		filename=$(basename "${file}")
		new_filename="${filename//_mot-opt3_/_mot-opt5_}"
		cp "${file}" "${dir}/${new_filename}" || echo "Failed to copy ${file}"
	done

	for file in "${fixed_effect_input}/ses-${session}/${sub}"/*_mot-opt4_*; do
		dir=$(dirname "${file}")
		filename=$(basename "${file}")
		new_filename="${filename//_mot-opt4_/_mot-opt6_}"
		cp "${file}" "${dir}/${new_filename}" || echo "Failed to copy ${file}"
	done
done

