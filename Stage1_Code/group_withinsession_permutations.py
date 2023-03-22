import os
from glob import glob
from pandas import DataFrame, read_csv
from nilearn.glm.second_level import SecondLevelModel

def group_onesample(fixedeffect_paths: list, session: str, task_type: str,
                    contrast: str, group_outdir: str,
                    model_permutation: str):
    """
    This function takes in a list of fixed effect files for a select contrast and
    calculates a group (secondlevel) model by fitting an intercept to length of maps.
    For example, for 10 subject maps of contrast A, the design matrix would include an intercept length 10.

    :param fixedeffect_paths: a list of paths to the fixed effect models to be used
    :param session: string session label, BIDS label e.g., ses-1
    :param task_type: string task label, BIDS label e.g., mid
    :param contrast: contrast type saved from fixed effect models
    :param model_permutation: complete string of model permutation, e.g., 'fwhm-4_mot-opt1_mod-AntMod'
    :param group_outdir: path to folder to save the group level models
    :return: nothing return, files are saved
    """

    if not os.path.exists(group_outdir):
        os.makedirs(group_outdir)
        print("Directory created:", group_outdir)

    N_maps = len(fixedeffect_paths)

    # Create design matrix with intercept (1s) that's length of subjects/length of fixed_files
    design_matrix = DataFrame([1] * N_maps,
                              columns=['Intercept'])

    # Fit secondlevel model
    sec_lvl_model = SecondLevelModel(smoothing_fwhm=None)
    sec_lvl_model = sec_lvl_model.fit(second_level_input=fixedeffect_paths,
                                      design_matrix=design_matrix)

    # Calculate z-statistic from second lvl map
    zstat_map = sec_lvl_model.compute_contrast(
        second_level_contrast='Intercept',
        second_level_stat_type='t',
        output_type='z_score',
    )

    # group out file, naming subs-N
    zstat_out = f'{group_outdir}/subs-{N_maps}_{session}_task-{task_type}_contrast-{contrast}_{model_permutation}' \
                f'_stat-zstat.nii.gz'
    zstat_map.to_filename(zstat_out)



# Set paths
local = '/Users/michaeldemidenko'
proj_loc = f'{local}/Desktop/Academia/Stanford/2_F32/Multiverse_Reliability'
data_dir = f'{local}/Downloads/test_modperm'
fix_dir = f'{data_dir}/FixedEffects/'
grp_out_dir = f'{data_dir}/Group_OneSample/'



# subjects, contrast & permutation list
subjects = read_csv(f'{proj_loc}/subjects.csv')['Subjects'].tolist()
sess = 'ses-01'
task = 'mid'
contrasts = [
    'Lgain-Neut','Sgain-Neut',
    'Lgain-Base','Sgain-Base'
]
permutation_list = read_csv(f'{proj_loc}/model_permutations.csv',
                            header=None, index_col=0).values.tolist()[1:]



# Running group level act. [uncorrected] for list of contrasts

for contrast in contrasts:
    print(f'\t Working on contrast map: {contrast}')
    for fwhm, motion, model, mask_type in permutation_list:
        model='mask-brain_mot-{}_mod-{}_fwhm-{}'.format(motion, model,fwhm)

        # find all contrast fixed effect maps for model permutation across subjects
        fix_maps = sorted(glob(f'{fix_dir}/*_{sess}_task-{task}_effect-fixed_'
                            f'contrast-{contrast}_{model}_stat-effect.nii.gz'))
        group_onesample(fixedeffect_paths=fix_maps, session=sess, task_type=task,
                        contrast=contrast, group_outdir=grp_out_dir,model_permutation=model)
