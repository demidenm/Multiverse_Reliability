import os
import argparse
import warnings
import numpy as np
import pandas as pd
from glob import glob
from itertools import product
from nilearn.glm import compute_fixed_effects
warnings.filterwarnings("ignore")


def fixed_effect(subject: str, session: str, task_type: str,
                 contrast_list: list, firstlvl_indir: str, fixedeffect_outdir: str,
                 model_permutation: str, save_beta=False, save_var=False, save_tstat=True):
    """
    This function takes in a subject, task label, set of computed contrasts using nilearn,
    the path to contrast estimates (beta maps), the output path for fixed effec tmodels and
    specification of types of files to save, the beta estimates, associated variance and t-stat (which is calculated
    based on beta/variance values)
    Several path indices are hard coded, so should update as see fit
    e.g., '{sub}_ses-{ses}_task-{task}_effect-fixed_contrast-{c}_stat-effect.nii.gz'

    :param subject: string-Input subject label, BIDS leading label, e.g., sub-01
    :param session: string-Input session label, BIDS label e.g., ses-1
    :param task_type: string-Input task label, BIDS label e.g., mid
    :param contrast_list: list of contrast types that are saved from first level
    :param model_permutation: complete string of model permutation, e.g., 'fwhm-4_mot-opt1_mod-AntMod'
    :param firstlvl_indir: string-location of first level output files
    :param fixedeffect_outdir: string-location to save fixed effects
    :param save_beta: Whether to save 'effects' or beta values, default = False
    :param save_var: Whether to save 'variance' or beta values, default = False
    :param save_tstat: Whether to save 'tstat', default = True
    :return: nothing return, files are saved
    """
    for contrast in contrast_list:
        betas = sorted(glob(f'{firstlvl_indir}/{subject}_ses-{session}_task-{task_type}_run-*_'
                            f'contrast-{contrast}_{model_permutation}_stat-beta.nii.gz'))

        var = sorted(glob(f'{firstlvl_indir}/{subject}_ses-{session}_task-{task_type}_run-*_'
                          f'contrast-{contrast}_{model_permutation}_stat-var.nii.gz'))

        # conpute_fixed_effects options
        # (1) contrast map of the effect across runs;
        # (2) var map of between runs effect;
        # (3) t-statistic based on effect of variance;
        fix_effect, fix_var, fix_tstat = compute_fixed_effects(contrast_imgs=betas,
                                                               variance_imgs=var,
                                                               precision_weighted=True)
        if not os.path.exists(fixedeffect_outdir):
            os.makedirs(fixedeffect_outdir)
            print("Directory created:", fixedeffect_outdir)

        if save_beta:
            fix_effect_out = f'{fixedeffect_outdir}/{subject}_ses-{session}_task-{task_type}_' \
                             f'contrast-{contrast}_{model_permutation}_stat-effect.nii.gz'
            fix_effect.to_filename(fix_effect_out)

        if save_var:
            fix_var_out = f'{fixedeffect_outdir}/{subject}_ses-{session}_task-{task_type}_' \
                          f'contrast-{contrast}_{model_permutation}_stat-var.nii.gz'
            fix_var.to_filename(fix_var_out)
        if save_tstat:
            fix_tstat_out = f'{fixedeffect_outdir}/{subject}_ses-{session}_task-{task_type}_' \
                            f'contrast-{contrast}_{model_permutation}_stat-tstat.nii.gz'
            fix_tstat.to_filename(fix_tstat_out)


parser = argparse.ArgumentParser(description="Script to run first level task models w/ nilearn")

parser.add_argument("--sample", help="sample type, abcd, AHRB, or mls?")
parser.add_argument("--sub", help="subject name, sub-XX, include entirety with 'sub-' prefix")
parser.add_argument("--task", help="task type -- e.g., mid, reward, etc")
parser.add_argument("--ses", help="session, include the session type without prefix, e.g., 1, 01, baselinearm1")
parser.add_argument("--firstlvl_inp", help="Path to first level directory")
parser.add_argument("--mask", help="path the to a binarized brain mask (e.g., MNI152 or "
                                 "constrained mask in MNI space",
                    default=None)
parser.add_argument("--mask_label", help="label for mask, e.g. mni152, subtresh, suprathresh, yeo-network",
                    default=None)
parser.add_argument("--output", help="output folder where to write out and save information")
parser.add_argument("--excl", help="TSV file with Subjects Inclusion(0)+exclusion for acompcor=1=",
                    default=None)

args = parser.parse_args()

# Now you can access the arguments as attributes of the 'args' object.
sample = args.sample
subj = args.sub
task = args.task
ses = args.ses
firstlvl_inp = args.firstlvl_inp
brainmask = args.mask
mask_label = args.mask_label
scratch_out = args.output
excl_list = args.excl

# contrast & permutation list
contrasts = [
    'Lgain-Neut', 'Sgain-Neut',
    'Lgain-Base', 'Sgain-Base'
]

# Model permutations
voxel_abcd_ahrb = 2.4
voxel_mls = 4
if sample in ['abcd', 'AHRB']:
    voxel = voxel_abcd_ahrb
    opts = np.array([1.5, 2, 2.5, 3, 3.5])
    fwhm_opt = list(np.round(voxel * opts, 1))
elif sample in 'MLS':
    voxel = voxel_mls
    inh_smooth_weight = .50
    opts = np.array([1.5, 2, 2.5, 3, 3.5]) * inh_smooth_weight
    fwhm_opt = list(np.round(voxel * opts, 1))

# only including 4; opt 5 is opt3 + subj mFD < .9 & opt6 is opt4 + subj mFD < .9
motion_opt = ["opt1", "opt2", "opt3", "opt4"]
modtype_opt = ["CueMod", "AntMod", "FixMod"]

permutation_list = list(product(fwhm_opt, motion_opt, modtype_opt))

# check exclusions
if excl_list is not None:
    # load excl df
    excl_subs = pd.read_csv(excl_list, sep='\t', header=None)
else:
    # empty DataFrame with 2 columns
    excl_subs = pd.DataFrame(columns=[0, 1])

count = 0
for fwhm, motion, model in permutation_list:
    exclude_subject = (
            excl_subs[excl_subs[0] == subj][1].values == "1" and
            motion in ["opt3", "opt4"]
    )
    if exclude_subject:
        print("{} aCompCor ROI flag excluded for model {}, {}, {}".format(subj, fwhm, motion, model))
    else:
        count = count + 1
        print('\t\t {}. Running model using: {}, {}, {}'.format(count, fwhm, motion, model))

        mod_name = f'mask-{mask_label}_mot-{motion}_mod-{model}_fwhm-{fwhm}'
        fixed_effect(subject=subj, session=ses, task_type=task,
                     contrast_list=contrasts, firstlvl_indir=firstlvl_inp, fixedeffect_outdir=scratch_out,
                     model_permutation=mod_name, save_beta=True, save_var=True, save_tstat=False)
