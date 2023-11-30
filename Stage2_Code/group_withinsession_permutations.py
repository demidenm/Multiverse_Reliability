import os
import warnings
import argparse
import pandas as pd
import numpy as np
from glob import glob
from nilearn.image import load_img, new_img_like
from nilearn.glm.second_level import SecondLevelModel
warnings.filterwarnings("ignore")

def nifti_tstat_to_cohensd(tstat_img, n):
    """
    function converts NIfTI t-statistic image to Cohen's d.

    :param tstat_img: NIfTI image containing t-statistics, Nifti1Image.
    :param n: Sample size for calculating Cohen's d, Integer
    :return: NIfTI image containing Cohen's d.
    """
    # Get data array from the t-statistics image
    t_data = tstat_img.get_fdata()
    # Calculate Cohen's d using the t_stat / sqrt(n) formula
    d_data = t_data / np.sqrt(n)
    # Create a NIfTI image containing Cohen's d, with the same properties as the input image
    cohensd_img = new_img_like(tstat_img, d_data)

    return cohensd_img


def group_onesample(fixedeffect_paths: list, session: str, task_type: str,
                    contrast_type: str, group_outdir: str,
                    model_permutation: str, level: str, mask: str = None):
    """
    This function takes in a list of fixed effect files for a select contrast and
    calculates a group (secondlevel) model by fitting an intercept to length of maps.
    For example, for 10 subject maps of contrast A, the design matrix would include an intercept length 10.

    :param fixedeffect_paths: a list of paths to the fixed effect models to be used
    :param session: string session label, BIDS label e.g., ses-1
    :param task_type: string task label, BIDS label e.g., mid
    :param contrast_type: contrast type saved from fixed effect models
    :param model_permutation: complete string of model permutation, e.g., 'fwhm-4_mot-opt1_mod-AntMod'
    :param level: run or group level map? e.g. run-01, run-02, ses-1 or ses-baselinearm1
    :param group_outdir: path to folder to save the group level models
    :param mask: path to mask, default none
    :return: nothing return, files are saved
    """

    if not os.path.exists(group_outdir):
        os.makedirs(group_outdir)
        print("Directory created:", group_outdir)

    N_maps = len(fixedeffect_paths)

    # Create design matrix with intercept (1s) that's length of subjects/length of fixed_files
    design_matrix = pd.DataFrame([1] * N_maps,
                                 columns=['Intercept'])

    # Fit secondlevel model
    sec_lvl_model = SecondLevelModel(mask_img=mask, smoothing_fwhm=None,minimize_memory=False)
    sec_lvl_model = sec_lvl_model.fit(second_level_input=fixedeffect_paths,
                                      design_matrix=design_matrix)

    # Calculate t-statistic from second lvl map, then convert to cohen's d
    tstat_map = sec_lvl_model.compute_contrast(
        second_level_contrast='Intercept',
        second_level_stat_type='t',
        output_type='stat'
    )

    # calculate residuals for group map
    residuals_grp = sec_lvl_model.residuals
    residual_out = f'{group_outdir}/subs-{N_maps}_ses-{session}_task-{task_type}_{level}_contrast-{contrast_type}' \
                  f'_{model_permutation}_stat-residuals.nii.gz'
    residuals_grp.to_filename(residual_out)

    # calc cohens d
    cohensd_map = nifti_tstat_to_cohensd(tstat_map, N_maps)
    # group out file, naming subs-N
    cohensd_out = f'{group_outdir}/subs-{N_maps}_ses-{session}_task-{task_type}_{level}_contrast-{contrast_type}' \
                f'_{model_permutation}_stat-cohensd.nii.gz'
    cohensd_map.to_filename(cohensd_out)


parser = argparse.ArgumentParser(description="Script to run first level task models w/ nilearn")
parser.add_argument("--sample", help="sample type, ahrb, abcd or mls?")
parser.add_argument("--task", help="task type -- e.g., mid, reward, etc")
parser.add_argument("--ses", help="session, include the session type without prefix, e.g., 1, 01, baselinearm1")
parser.add_argument("--type", help="type of group -- run-01 or session-baselinearm1")
parser.add_argument("--model", help="model permutation,"
                                    " e.g. contrast-Sgain-Neut_mask-mni152_mot-opt5_mod-FixMod_fwhm-6.0")
parser.add_argument("--mask", help="path the to the binarized brain mask (e.g., MNI152 or "
                                   "constrained mask in MNI space, or None")
parser.add_argument("--mask_label", help="label for mask, e.g. subtresh, suprathresh, yeo-network, or None")
parser.add_argument("--input", help="input path to data")
parser.add_argument("--output", help="output folder where to write out and save information")

args = parser.parse_args()

# Now you can access the arguments as attributes of the 'args' object.
sample = args.sample
task = args.task
ses = args.ses
type = args.type
brainmask = args.mask
mask_label = args.mask_label
model = args.model
fix_dir = args.input
scratch_out = args.output

# contrasts
contrasts = [
    'Lgain-Neut', 'Sgain-Neut',
    'Lgain-Base', 'Sgain-Base'
]

for contrast in contrasts:
    print(f'\t Working on contrast map: {contrast}')

    # find all contrast fixed effect maps for model permutation across subjects
    fix_maps = sorted(glob(f'{fix_dir}/*_ses-{ses}_task-{task}_*'
                           f'contrast-{contrast}_{model}_stat-effect.nii.gz'))
    group_onesample(fixedeffect_paths=fix_maps, session=ses, task_type=task,
                    contrast_type=contrast, group_outdir=scratch_out,
                    model_permutation=model, mask=brainmask, level=type)
