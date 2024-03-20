# Cluster Jobs README file

SLURM submission animated gif for AHRB data on Sherlock:
![sbatch submission gif](./templates/animated_submissions.gif)

## Templates

There are several template files used for the three samples. ABCD differs as it uses MSI and has calibration volumes to trip. 
AHRB/MLS are similar, exclusion on TR/N vols, task label and how sessions for MLS are used.

**First level**: templates to run batch jobs for each subject
  - abcd_firstlvl.txt sets n_vols, tr_sec, stc correction, location for behavioral data, mask_path, folders for each out/in dir. Pulls from s3 and curates data
  - ahrb_firstlvl.txt sets n_vols, tr_sec, stc correction, location for behavioral data, mask_path, folders for each out/in dir. Pulls from OAK dir and curates data
  - mls_firstlvl.txt fsets n_vols, tr_sec, stc correction, location for behavioral data, mask_path, folders for each out/in dir. Pulls from OAK dir and curates data

**Group models**: templates to run batch jobs for each group model permutation
  - group.txt: for MSI/ABCD
  - group_sherlock.txt: for AHRB/MLS on Sherlock

**ICC models**: templates to run batch jobs for each ICC model
  - abcd_icc.txt
  - icc_sherlock.txt

## Make files

There are several make files that are used to make SLURM jobs for each type of run. 
Besides session/task labels and inp/output paths, ABCD/AHRB/MLS use a similar make submission process. The script is called ./make_abcd-first.sh <file> <file>.
The example below is for ABCD only, to not be redundant.

**make_abcd-first.sh**: Making first level SLURM jobs for each subject (runtime, 90-120min each)

- **Input Parameters**: The script takes two arguments:
  - A file of subject IDs (.tsv) with the "sub-" prefix.
  - A TSV file containing subject IDs with corresponding ACOMPCOR exclusion flags (e.g. column 2 contains 1 = exclude, 0 = dont exclude.

- **Parameter Configuration**: Running analsis_type=MULTIVERSE runs all models. Running "single" runs specified FWHM, motion, model. Provide session & output directory.
  - `subject_ids`: path to subject list.
  - `acomp_list`: path to acompcor file (no header). Col1 sub-* IDs, col2 exclusion 1 or non-exclusion 0
  - `run`: Specifies the run number (e.g., 1, 2 or None).
  - `ses`: Specifies the session (e.g., "baselineYear1Arm1" or "2YearFollowUpYArm1").
  - `analysis_type`: Specifies the type of analysis ("MULTIVERSE" or "single").
    - If single: `fwhm`, `motion`, `modtype` used
  - `out_dir`: Specifies the output directory.
  - `count_start`: Specifies the starting counter for batch job scripts.

Individual run files output to ./batch_jobs/first* created based on ./templates/abcd_firstlvl.txt and submitted using `first_msi.batch`

**make_abcd-group.sh:**: making individual slurm jobs for group models for model permutations for run and session level outputs (runtime 3-5min each)

- **Input Parameters**: The script takes one argument
  - The script requires a subject file (.tsv) with the "sub-" prefix as its first argument.

- **Parameter Configuration**: 
  - `sample`: Specifies the dataset (e.g., "abcd").
  - `task`: Specifies the task (e.g., "MID").
  - `run`: Specifies the run number (e.g., 1, 2 or None).
  - `ses`: Specifies the session (e.g., "baselineYear1Arm1" or "2YearFollowUpYArm1").
  - `type`: Specifies the type of analysis ("session" or "run").
  - `outfold`: Specifies the output directory.
  - `counter_start`: Specifies the starting counter for batch job scripts.

- **Model Permutations**:
  - Various model permutations are specified based on the dataset (`sample`) chosen.
  - Parameters such as FWHM, motion, and model type are configured based on the dataset.

Individual run files output to ./batch_jobs/group* based on ./templates/group.txt and submitted using `group_msi.batch`

**make_abcd-icc.sh:** making individual SLURM jobs for ICC jobs for each model type (runtime, 12-18min each)
- **Input Parameters**: 
  - `sample`: Specifies the dataset (e.g., "abcd", "ahrb", or "mls").
  - `ses`: Specifies the session (e.g., "baselineYear1Arm1" or "2YearFollowUpArm1").
  - `mask_label`: Specifies the mask label (e.g., "None", "wilson-sub", "wilson-supra").
  - `type`: Specifies the type of analysis ("run" or "session").
  - `subj_ids`: Specifies the subject IDs.

Individual run files output to ./batch_jobs/icc* based on ./templates/abcd_icc.txt and submitted using `icc_msi.batch`

**make_abcd-icc-sub.sh:** Make SLURM jobs for each seed to run subsampling on N 25 to 525 interval of 50.

- **Input Parameters**: 
  - `ses`: Specifies the session (e.g., "baselineYear1Arm1" or "2YearFollowUpArm1").
  - `task`: Specifies the task (e.g., "MID").
  - `model`: Specifies the model to be used for ICC analysis (e.g.contrast-Lgain-Base_mask-mni152_mot-opt2_mod-CueMod_fwhm-8.4)
  - `min`: Specifies the min number of subjects to be subsampled.
  - `max`: Specifies the max number of subjects to be subsampled.
  - `subj_ids`: Specifies the file for subject IDs.
  - `seed_list`: Specifies the file for list of seeds for subsampling.


Individual run files output to ./batch_jobs/icc* based on ./templates/abcd_icc-subsample.txt submitted with icc_msi.batch
