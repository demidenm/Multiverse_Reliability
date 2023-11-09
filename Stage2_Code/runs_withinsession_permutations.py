import os
import argparse
from glob import glob
from itertools import product
from nilearn.glm import compute_fixed_effects


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
        betas = sorted(glob(f'{firstlvl_indir}/**/{subject}_{session}_task-{task_type}_run-*_'
                            f'contrast-{contrast}_{model}_stat-beta.nii.gz'))

        var = sorted(glob(f'{firstlvl_indir}/**/{subject}_{session}_task-{task_type}_run-*_'
                          f'contrast-{contrast}_{model}_stat-var.nii.gz'))

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
                             f'effect-fixed_contrast-{contrast}_{model_permutation}_stat-effect.nii.gz'
            fix_effect.to_filename(fix_effect_out)

        if save_var:
            fix_var_out = f'{fixedeffect_outdir}/{subject}_ses-{session}_task-{task_type}_' \
                          f'effect-fixed_contrast-{contrast}_{model_permutation}_stat-var.nii.gz'
            fix_var.to_filename(fix_var_out)
        if save_tstat:
            fix_tstat_out = f'{fixedeffect_outdir}/{subject}_ses-{session}_task-{task_type}_' \
                            f'effect-fixed_contrast-{contrast}_{model_permutation}_stat-tstat.nii.gz'
            fix_tstat.to_filename(fix_tstat_out)


parser = argparse.ArgumentParser(description="Script to run first level task models w/ nilearn")

parser.add_argument("sample", help="sample type, ahrb, abcd or mls?")
parser.add_argument("sub", help="subject name, sub-XX, include entirety with 'sub-' prefix")
parser.add_argument("task", help="task type -- e.g., mid, reward, etc")
parser.add_argument("ses", help="session, include the session type without prefix, e.g., 1, 01, baselinearm1")
parser.add_argument("firstlvl_inp", help="Path to first level directory")
parser.add_argument("mask", help="path the to a binarized brain mask (e.g., MNI152 or "
                                 "constrained mask in MNI space, or None")
parser.add_argument("mask_label", help="label for mask, e.g. subtresh, suprathresh, yeo-network, or None")
parser.add_argument("output", help="output folder where to write out and save information")

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

# contrast & permutation list
contrasts = [
    'Lgain-Neut', 'Sgain-Neut',
    'Lgain-Base', 'Sgain-Base'
]

fwhm_opt = [4,  5]
mot_opt = ["opt1", "opt5"]
modtype_opt = ["AntMod", "FixMod"]

# note, didn't save in FirstLvl due to need smoothing to occur outside of list
model_permutations = list(product(fwhm_opt, mot_opt, modtype_opt))

count = 0
for fwhm, motion, model in model_permutations:
    count = count + 1
    print('\t\t {}. Running model using: {}, {}, {}'.format(count, fwhm, motion, model))

    model = f'mask-{mask_label}_mot-{motion}_mod-{model}_fwhm-{fwhm}'
    fixed_effect(subject=subj, session=ses, task_type=task,
                 contrast_list=contrasts, firstlvl_indir=firstlvl_inp, fixedeffect_outdir=scratch_out,
                 model_permutation=model, save_beta=True, save_var=True, save_tstat=False)
