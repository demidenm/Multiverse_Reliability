import os
import time
from glob import glob
from pandas import read_csv, DataFrame
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
    e.g., '{sub}_ses-01_task-{task_type}_effect-fixed_contrast-{c}_stat-effect.nii.gz'

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
        betas = sorted(glob(f'{firstlvl_indir}/{subject}_{session}_task-{task_type}_run-*_'
                            f'contrast-{contrast}_{model}_beta.nii.gz'))

        var = sorted(glob(f'{firstlvl_indir}/{subject}_{session}_task-{task_type}_run-*_'
                            f'contrast-{contrast}_{model}_var.nii.gz'))

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

        if save_beta == True:
            fix_effect_out = f'{fixedeffect_outdir}/{subject}_{session}_task-{task_type}_' \
                             f'effect-fixed_contrast-{contrast}_{model_permutation}_stat-effect.nii.gz'
            fix_effect.to_filename(fix_effect_out)

        if save_var == True:
            fix_var_out = f'{fixedeffect_outdir}/{subject}_{session}_task-{task_type}_' \
                          f'effect-fixed_contrast-{contrast}_{model_permutation}_stat-var.nii.gz'
            fix_var.to_filename(fix_var_out)
        if save_tstat == True:
            fix_tstat_out = f'{fixedeffect_outdir}/{subject}_{session}_task-{task_type}_' \
                            f'effect-fixed_contrast-{contrast}_{model_permutation}_stat-tstat.nii.gz'
            fix_tstat.to_filename(fix_tstat_out)



# Set paths
local = '/Users/michaeldemidenko'
proj_loc = f'{local}/Desktop/Academia/Stanford/2_F32/Multiverse_Reliability'
data_dir = f'{local}/Downloads/test_modperm'
in_dir = f'{data_dir}/Firstlvl/'
fix_dir = f'{data_dir}/FixedEffects/'



# subjects, contrast & permutation list
subjects = read_csv(f'{proj_loc}/subjects.csv')['Subjects'].tolist()
contrasts = [
    'Lgain-Neut','Sgain-Neut',
    'Lgain-Base','Sgain-Base'
]

# create save permutation list
fwhm = [4,5]
mot = ["opt1", "opt5"]
mod_type = ["AntMod", "FixMod"]

# note, didn't save in FirstLvl due to need smoothing to occur outside of list
model_permutations = DataFrame(data=list(product(fwhm, mot, mod_type)),
                               columns=["fwhm","motion","mod_type"])
model_permutations.to_csv(f'{proj_loc}/model_permutations.csv')
permutation_list = read_csv(f'{proj_loc}/model_permutations.csv',
                            header=None, index_col=0).values.tolist()[1:]

# running fixed effect model (effect across two runs) for all model permutations
for subj in subjects:
    start_time = time.time()
    print(f'\t Working on subject: {subj}')
    for fwhm, motion, model in permutation_list:
        print('\t\t Running model using: {}, {}, {}'.format(fwhm, motion, model))

        model='mask-brain_mot-{}_mod-{}_fwhm-{}'.format(motion, model,fwhm)
        fixed_effect(subject=subj, session='ses-01', task_type='mid',
                     contrast_list=contrasts,firstlvl_indir=in_dir, fixedeffect_outdir=fix_dir,
                     model_permutation=model, save_beta = True, save_var = True, save_tstat = False)

    end_time = time.time()
    print('\t ** Fixed Effect Permutations Completed.'
          'Total runtime in minutes: {}'.format((end_time - start_time) / 60))

