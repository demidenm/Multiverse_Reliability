import warnings
import argparse
import nibabel as nib
import random
from pyrelimri import brain_icc
warnings.filterwarnings("ignore")

# running below after 100 random seeds are generated using
# random.seed(100); [random.randint(1,10000) for _ in range(100)]

parser = argparse.ArgumentParser(description="Script to run ICC subsampling across N")
parser.add_argument("--ses", help="session, include the session type without prefix, e.g., 1, 01, baselinearm1")
parser.add_argument("--task", help="task mid, MID, or reward")
parser.add_argument("--model", help="model info, e.g. contrast, mot, fwhm, etc")
parser.add_argument("--min_n", help="Starting N")
parser.add_argument("--max_n", help="ending N")
parser.add_argument("--sub_list", help="subject list to subsample from")
parser.add_argument("--mask", help="path the to a binarized brain mask (e.g., MNI152 or "
                                   "constrained mask in MNI space, spec-network; default None",
                    default=None)
parser.add_argument("--inp_path", help="Path to the output directory for the fmriprep derivatives")
parser.add_argument("--output", help="output folder where to write out and save information")
parser.add_argument("--seed", help="set seed for reproducibility of random choice")
args = parser.parse_args()

# Now you can access the arguments as attributes of the 'args' object.
ses = args.ses
task = args.task
model = args.model
min_n = int(args.min_n)
max_n = int(args.max_n)
subject_list = args.sub_list
mask = args.mask
inp_path = args.inp_path
out_path = args.output
seed = int(args.seed)

# read in subject list
with open(subject_list, "r") as file:
    # read in subject lines
    subj_ids = file.readlines()

sublist_clean = [line.strip() for line in subj_ids]

# create n range with interval
n_int = 50
n_range = list(range(min_n, max_n+n_int, n_int))

random.seed(seed)
for subj_n in n_range:
    subsample_id = random.choices(sublist_clean, k=subj_n)
    print(f"Of the {len(subsample_id)} subject IDs, n = {len(set(subsample_id))} are unique")

    set1 = [f'{inp_path}/ses-{ses}/{subj_id}/{subj_id}_ses-{ses}_task-{task}_run-01_{model}_stat-beta.nii.gz' for subj_id in subsample_id]
    set2 = [f'{inp_path}/ses-{ses}/{subj_id}/{subj_id}_ses-{ses}_task-{task}_run-02_{model}_stat-beta.nii.gz' for subj_id in subsample_id]

    assert len(set1) > 0 and len(set2) > 0, f'Length of set1 [{len(set1)}] and/or set2 [{len(set2)}] is zero.'
    assert len(set1) == len(set2), f'Lengths of set1 [{len(set1)}] and set2 [{len(set2)}] are not equal.'
    match_string_position = all(
        a.split('_')[0:3] == b.split('_')[0:3] and a.split('_')[5:] == b.split('_')[5:] for a, b in zip(set1, set2))
    assert match_string_position, "Values at path-positions 2:3 and 5: do not match."

    print(f"Running ICC(3,1) on {len(set1)} subjects")
    brain_models = brain_icc.voxelwise_icc(multisession_list=[set1, set2],
                                           mask=mask, icc_type='icc_3')
    for img_type in ['est', 'btwnsub', 'wthnsub']:
        out_icc_path = f'{out_path}/seed-{seed}_subs-{len(set1)}_task-MID_type-run_{model}_stat-{img_type}.nii.gz'
        nib.save(brain_models[img_type], out_icc_path)
