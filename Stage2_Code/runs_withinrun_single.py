import warnings
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=UserWarning,
                        message="A NumPy version >=1.18.5 and <1.25.0 is required for this version of SciPy*")
import sys
import os
import argparse
import pandas as pd
from glob import glob
from nilearn.glm.first_level import FirstLevelModel



# Getpath to Stage2 scripts
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_dir)
from Stage2_Code.designmat_regressors_define import create_design_mid, pull_regressors

# relabel column names to match templates code for ABCD/MLS
dict_renamecols_abcd = {
    'Cue.OnsetTime': 'CUE_ONSET',
    'Cue.Duration': 'CUE_DURATION',
    'Anticipation.OnsetTime': 'FIXATION_ONSET',
    'Anticipation.Duration': 'FIXATION_DURATION',
    'Feedback.OnsetTime': 'FEEDBACK_ONSET',
    'FeedbackDuration': 'FEEDBACK_DURATION',
    'Condition': 'TRIAL_TYPE',
    'Result': 'TRIAL_RESULT'
}

dict_renamecols_mls = {
    'Cue.OnsetTime': 'CUE_ONSET',
    'Cue.Duration': 'CUE_DURATION',
    'Fix.OnsetTime': 'FIXATION_ONSET',
    'Fix.Duration': 'FIXATION_DURATION',
    'Feedback.OnsetTime': 'FEEDBACK_ONSET',
    'Feedback.Duration': 'FEEDBACK_DURATION',
    'Condition': 'TRIAL_TYPE',
    'Result': 'TRIAL_RESULT'
}

dict_rename_cuetype = {
        'LgReward': 'LargeGain',
        'LgPun': 'LargeLoss',
        'Triangle': 'NoMoneyStake',
        'SmallReward': 'SmallGain',
        'SmallPun': 'SmallLoss'
}

parser = argparse.ArgumentParser(description="Script to run first level task models w/ nilearn")

parser.add_argument("--sample", help="sample type, abcd, AHRB, MLS?")
parser.add_argument("--sub", help="subject name, sub-XX, include entirety with 'sub-' prefix")
parser.add_argument("--task", help="task type -- e.g., mid, reward, etc")
parser.add_argument("--ses", help="session, include the session type without prefix, e.g., 1, 01, baselinearm1")
parser.add_argument("--stc", help="slice time correction performed or not during preprocessing? False (no), True (yes)")
parser.add_argument("--numvols", help="The number of volumes for BOLD file, e.g numeric")
parser.add_argument("--boldtr", help="the tr value for the datasets in seconds, e.g. .800, 2.0, 3.0")
parser.add_argument("--fwhm", help="smoothing kernal, fwhm mm, e.g 4.6")
parser.add_argument("--motion", help="motion type, e.g., opt1, opt2, opt3, opt4")
parser.add_argument("--modtype", help="design model type, e.g. CueMod, AntMod, FixMod")
parser.add_argument("--beh_path", help="Path to the behavioral (.tsv) directory/files for the task")
parser.add_argument("--fmriprep_path", help="Path to the output directory for the fmriprep output")
parser.add_argument("--mask", help="path the to a binarized brain mask (e.g., MNI152 or "
                                   "constrained mask in MNI space, spec-network",
                    default=None)
parser.add_argument("--mask_label", help="label for mask, e.g. mni152, subtresh, suprathresh, yeo-network",
                    default=None)
parser.add_argument("--output", help="output folder where to write out and save information")


args = parser.parse_args()

# Now you can access the arguments as attributes of the 'args' object.
sample = args.sample
subj = args.sub
task = args.task
stc = args.stc
ses = args.ses
fwhm_opt = float(args.fwhm)
motion_opt = args.motion
modtype_opt = args.modtype
numvols = int(args.numvols)
boldtr = float(args.boldtr)
beh_path = args.beh_path
fmriprep_path = args.fmriprep_path
brainmask = args.mask
mask_label = args.mask_label
scratch_out = args.output

# model design options, contrasts and weights setup
model_types = {
    "AntMod": ['CUE_ONSET', "ANTICIPATION_DURATION"],
    "FixMod": ['FIXATION_ONSET', "FIXATION_DURATION"],
    "CueMod": ['CUE_ONSET', 'CUE_DURATION']
}

contrasts = {
    'Lgain-Neut': 'LargeGain - NoMoneyStake',
    'Sgain-Neut': 'SmallGain - NoMoneyStake',
    'Lgain-Base': 'LargeGain',
    'Sgain-Base': 'SmallGain',
}

contrast_weights = {
    'Lgain-Neut': {'LargeGain': 1, 'NoMoneyStake': -1},
    'Sgain-Neut': {'SmallGain': 1, 'NoMoneyStake': -1},
    'Lgain-Base': {'LargeGain': 1},
    'Sgain-Base': {'SmallGain': 1}
}

runs = ['01', '02']

for run in runs:
    print(f'\tStarting {subj} {run}.')

    print('\t\t Running model using: {}, {}, {}'.format(fwhm_opt, motion_opt, modtype_opt))
    print('\t\t 1/4 Load Files & set paths')
    # import behavior events .tsv from data path
    events_df = pd.read_csv(f'{beh_path}/{subj}/ses-{ses}/func/{subj}_ses-{ses}_task-{task}_run-{run}_events.tsv',
                            sep='\t')
    if sample == 'abcd':
        events_df = events_df.rename(columns=dict_renamecols_abcd)
        events_df['TRIAL_TYPE'] = events_df['TRIAL_TYPE'].replace(dict_rename_cuetype)
    elif sample == 'MLS':
        events_df = events_df.rename(columns=dict_renamecols_mls)
        events_df['TRIAL_TYPE'] = events_df['TRIAL_TYPE'].replace(dict_rename_cuetype)
    else:
        print("Assuming AHRB sample, continuing")
    # get path to confounds from fmriprep, func data + mask
    # set image path
    conf_path = f'{fmriprep_path}/{subj}/ses-{ses}/func/{subj}_ses-{ses}_task-{task}_run-{run}' \
            f'_desc-confounds_timeseries.tsv'
    nii_path = glob(
    f'{fmriprep_path}/{subj}/ses-{ses}/func/{subj}_ses-{ses}_task-{task}_run-{run}'
    f'_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz')[0]
    print('\t\t 2/4 Create Regressors & Design Matrix for GLM')
    # get list of regressors
    # run to create design matrix
    conf_regressors = pull_regressors(confound_path=conf_path, regressor_type=motion_opt, sample=sample)
    design_matrix = create_design_mid(events_df=events_df, bold_tr=boldtr, num_volumes=numvols,
                                      onset_label=model_types[modtype_opt][0],
                                      duration_label=model_types[modtype_opt][1],
                                      conf_regressors=conf_regressors,
                                      hrf_model='spm', stc=stc)

    print('\t\t 3/4 Mask Image, Fit GLM model ar1 autocorrelation')
    # using ar1 autocorrelation (FSL prewhitening), drift model
    fmri_glm = FirstLevelModel(subject_label=subj, mask_img=brainmask,
                               t_r=boldtr, smoothing_fwhm=fwhm_opt,
                               standardize=False, noise_model='ar1', drift_model=None, high_pass=None
                               # cosine 0:3 included from fmriprep in design mat based on 128s calc
                               )
    # Run GLM model using set paths and calculate design matrix
    run_fmri_glm = fmri_glm.fit(nii_path, design_matrices=design_matrix)
    print('\t\t 5/5: From GLM model, create z-score contrast maps and save to output path')
    # contrast names and associated contrasts in contrasts defined is looped over
    # contrast name is used in saving file, the contrast is used in deriving z-score
    for con_name, con in contrasts.items():
        mod_name = f'contrast-{con_name}_mask-{mask_label}_mot-{motion_opt}_mod-{modtype_opt}_fwhm-{fwhm_opt}'
        beta_name = f'{scratch_out}/{subj}_ses-{ses}_task-{task}_run-{run}_{mod_name}_stat-beta.nii.gz'
        beta_est = run_fmri_glm.compute_contrast(con, output_type='effect_size')
        beta_est.to_filename(beta_name)
        # Calc: variance
        var_name = f'{scratch_out}/{subj}_ses-{ses}_task-{task}_run-{run}_{mod_name}_stat-var.nii.gz'
        var_est = run_fmri_glm.compute_contrast(con, output_type='effect_variance')
        var_est.to_filename(var_name)
