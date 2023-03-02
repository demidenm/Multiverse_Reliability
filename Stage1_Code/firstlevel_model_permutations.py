import os
import time
from pandas import read_csv, DataFrame
from glob import glob
from Stage1_Code.designmat_regressors_define import create_design_mid,pull_regressors
from nilearn.glm.first_level import FirstLevelModel
from itertools import product

local = '/Users/michaeldemidenko'
proj_loc = f'{local}/Desktop/Academia/Stanford/2_F32/Multiverse_Reliability'

# Model options
fwhm = [4, 7]
mot = ["opt1", "opt3"]
mod_type = ["AntMod", "FixMod"]

#Create permutations across options and save for list
model_permutations = DataFrame(data=list(product(fwhm, mot, mod_type)),columns=["fwhm","motion","mod_type"])
model_permutations.to_csv(f'{proj_loc}/model_permutations.csv')

model_types = {
    "AntMod": ['CUE_ONSET', "ANTICIPATION_DURATION"],
    "FixMod": ['FIXATION_ONSET', "FIXATION_DURATION"],
    "CueMod": ['CUE_ONSET', 'CUE_DURATION']
}

# defining input (fmriprep) and output paths
sher_path = f'{local}/sherlock/data/AHRB'
deriv_path = f'{local}/Desktop/Academia/Stanford/2_F32/Data/Pilot_N1/derivatives/fmri_prep'
firstlvl_output = f'{local}/Downloads/test_modperm/Firstlvl'

if not os.path.exists(firstlvl_output):
    os.makedirs(firstlvl_output)
    print("Directory created:", firstlvl_output)

# Creating list of subjects, runs & models to loop over
subjects = read_csv(f'{proj_loc}/subjects.csv')['Subjects'].tolist()
runs = ['run-01', 'run-02']
permutation_list = read_csv(f'{proj_loc}/model_permutations.csv',
                            header=None, index_col=0).values.tolist()[1:]


contrasts = {
    'Lgain-Neut': 'LargeGain - NoMoneyStake',
    'Sgain-Neut': 'SmallGain - NoMoneyStake',
    'Lgain-Base': 'LargeGain',
    'Sgain-Base': 'SmallGain',
}

# provide TR & volumes for associated BOLD
boldtr = .8
numvols = 407


for subj in subjects:
    start_time = time.time()
    for run in runs:
        print(f'\tStarting {subj} {run}.')
        for smooth, motion, model in permutation_list:
            print(f'\t\t 1/4 Load Files & set paths')
            # import behavior events .tsv from data path
            events_df = read_csv(f'{sher_path}/{subj}/ses-1/func/{subj}_ses-1_task-mid_{run}_events.tsv', sep='\t')

            # get path to confounds from fmriprep, func data + mask
            conf_path = f'{deriv_path}/{subj}/ses-1/func/{subj}_ses-1_task-mid_{run}_desc-confounds_timeseries.tsv'
            mask_path = glob(
                f'{deriv_path}/{subj}/ses-1/func/{subj}_ses-1_task-mid_{run}'
                f'_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'
            )[0]
            nii_path = glob(
                f'{deriv_path}/{subj}/ses-1/func/{subj}_ses-1_task-mid_{run}'
                f'_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz'
            )[0]

            print(f'\t\t 2/4 Create Regressors & Design Matrix for GLM')
            # get list of regressors
            conf_regressors = pull_regressors(confound_path=conf_path, regressor_type=motion)

            # run to create design matrix
            design_matrix = create_design_mid(events_df=events_df, bold_tr=boldtr, num_volumes=numvols,
                                       onset_label=model_types[model][0],
                                       duration_label=model_types[model][1],
                                       conf_regressors=conf_regressors,
                                       hrf_model='glover', stc=False)

            print(f'\t\t 3/4 Fit GLM model ar1 autocorrelation')
            # fitting glm for sub's run, using associated mask,
            # using ar1 autocorrelation (FSL prewhitening), drift model
            fmri_glm = FirstLevelModel(subject_label={subj}, mask_img=mask_path, t_r=boldtr, smoothing_fwhm=int(smooth),
                                       standardize=False, noise_model='ar1', drift_model=None, high_pass=None
                                       # cosine 0:3 included from fmriprep in desing mat based on 128 s calc
                                       )

            # Run GLM model using set paths and calculate design matrix
            run_fmri_glm = fmri_glm.fit(nii_path, design_matrices=design_matrix)

            print(f'\t\t 4/4: From GLM model, create z-score contrast maps and save to output path')
            # contrast names and associated contrasts in contrasts defined is looped over
            # contrast name is used in saving file, the contrast is used in deriving z-score
            for con_name, con in contrasts.items():
                beta_name = f'{firstlvl_output}/{subj}_ses-01_task-mid_{run}_contrast-{con_name}_fwhm-{smooth}' \
                            f'_mot-{motion}_mod-{model}_beta.nii.gz'
                beta_est = run_fmri_glm.compute_contrast(con, output_type='effect_size')
                beta_est.to_filename(beta_name)

                # Calc: variance
                var_name = f'{firstlvl_output}/{subj}_ses-01_task-mid_{run}_contrast-{con_name}_fwhm-{smooth}' \
                           f'_mot-{motion}_mod-{model}_var.nii.gz'
                var_est = run_fmri_glm.compute_contrast(con, output_type='effect_variance')
                var_est.to_filename(var_name)

    end_time = time.time()
    print('\t ** Total runtime: {}'.format(end_time - start_time))
