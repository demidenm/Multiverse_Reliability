import os
import argparse
import warnings
import nibabel as nib
from glob import glob
from pyrelimri import brain_icc
from nilearn import image, datasets

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description="Script to run first level task models w/ nilearn")
parser.add_argument("--sample", help="sample type, ahrb, abcd or mls?")
parser.add_argument("--ses", help="session, include the session type without prefix, e.g., 1, 01, baselinearm1")
parser.add_argument("--type", help="between runs or sessions, e.g., run, session")
parser.add_argument("--model", help="model permutation, e.g. contrast-Sgain-Neut_mask-mni152_mot-opt5_mod-FixMod_fwhm-6.0")
parser.add_argument("--mask", help="path the to a binarized brain mask (e.g., MNI152 or "
                                   "constrained mask in MNI space, spec-network, or None")
parser.add_argument("--mask_label", help="label for mask, e.g. mni152, wilson-supra, wilson-sub, yeo-network, or None")
parser.add_argument("--inp_path", help="Path to the output directory for the fmriprep output")
parser.add_argument("--output", help="output folder where to write out and save information")
args = parser.parse_args()

# Now you can access the arguments as attributes of the 'args' object.
sample = args.sample
ses = args.ses
model = args.model
type = args.type
mask = args.mask
mask_label = args.mask_label
inp_path = args.inp_path
out_path = args.output


# download neurovault mask if sub and suprathresh masks dont exist
if not os.path.exists(mask):
    mask_dir = os.path.dirname(mask)
    # Load the Wilson image
    wilson_img = datasets.fetch_neurovault_ids(image_ids=[68843])
    wilson = image.load_img(wilson_img.images[0])
    wilson_resample = image.resample_to_img(source_img=wilson,
                                            target_img=f'{mask_dir}/MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz',
                                            interpolation='continuous')

    # binarize masked image
    threshold = 3.1

    for thresh in ['supra', 'sub']:
        if thresh == 'supra':
            thresh_bin = (wilson_resample.get_fdata() > threshold).astype(int)
            thresh_mask_img = nib.Nifti1Image(thresh_bin, wilson_resample.affine)
            output_path = f'{mask_dir}/MNI152_wilson-{thresh}.nii.gz'
            nib.save(thresh_mask_img, output_path)
        else:
            thresh_bin = (wilson_resample.get_fdata() < threshold).astype(int)
            mni_mask = nib.load(mask)
            thresh_bin *= mni_mask.get_fdata().astype(int)
            thresh_mask_img = nib.Nifti1Image(thresh_bin, wilson_resample.affine)
            output_path = f'{mask_dir}/MNI152_wilson-{thresh}.nii.gz'
            nib.save(thresh_mask_img, output_path)


if 'run' == type:
    set1 = sorted(glob(f'{inp_path}/ses-{ses}/**/*_ses-{ses}_task-MID_run-01_{model}_stat-beta.nii.gz'))
    set2 = sorted(glob(f'{inp_path}/ses-{ses}/**/*_ses-{ses}_task-MID_run-02_{model}_stat-beta.nii.gz'))
    assert len(set1) > 0 and len(set2) > 0, f'Length of set1 [{len(set1)}] and/or set2 [{len(set2)}] is zero.'
    assert len(set1) == len(set2), f'Lengths of set1 [{len(set1)}] and set2 [{len(set2)}] are not equal.'
    match_string_position = all(
        a.split('_')[1:3] == b.split('_')[1:3] and a.split('_')[5:] == b.split('_')[5:] for a, b in zip(set1, set2))
    assert match_string_position, "Values at path-positions 2:3 and 5: do not match."

elif 'session' == type:
    session_list = os.listdir()
    set1 = sorted(glob(f'{inp_path}/{session_list[0]}/**/*_{session_list[0]}_task-MID_{model}_stat-effect.nii.gz'))
    set2 = sorted(glob(f'{inp_path}/{session_list[1]}/**/*_{session_list[1]}_task-MID_{model}_stat-effect.nii.gz'))
    assert len(set1) == len(set2), f'Lengths of set1 [{len(set1)}] and set2 [{len(set2)}] are not equal.'
else:
    print("incorrect reliability type provided. Options run and session")


brain_models = brain_icc.voxelwise_icc(multisession_list = [set1, set2],
                                        mask=mask, icc_type='icc_3')

for img_type in ['est', 'msbtwn', 'mswthn']:
    out_icc_path = f'{out_path}/subs-{len(set1)}_type-{type}_mask-{mask_label}_{model}_stat-{img_type}.nii.gz'
    nib.save(brain_models[img_type], out_icc_path)