import pandas as pd
import json
import sys
import os

# specify arguments
input_dir=sys.argv[1]
subject = sys.argv[2]
ses = sys.argv[3]
task = sys.argv[4]

deriv_path = f'{input_dir}/{subject}/ses-{ses}/func'
# read in list of IDs/ses to summarize
if os.path.exists(f'{deriv_path}/task-{task}_summ-mot-acc-rt.csv'):
    existing_df = pd.read_csv(f'{deriv_path}/task-{task}_summ-mot-acc-rt.csv')
else:
    # Create an empty DataFrame with the desired columns if the file doesn't exist
    existing_df = pd.DataFrame(columns=['Subject', 'Session', 'mFD_run1', 'mFD_run2', 'acc_run1', 'acc_run2', 'mrt_run1', 'mrt_run2'])

# Loop through subjects and sessions

# assign dirs to pull from
file_path_run1 = f'{deriv_path}/{subject}_ses-{ses}_task-{task}_run-01_desc-confounds_timeseries.tsv'
file_path_run2 = f'{deriv_path}/{subject}_ses-{ses}_task-{task}_run-02_desc-confounds_timeseries.tsv'

# Read the TSV files into pandas DataFrames
df_run1 = pd.read_csv(file_path_run1, delimiter='\t')
df_run2 = pd.read_csv(file_path_run2, delimiter='\t')

# Calculate the mean framewise displacement for run-01/run-02
mean_fd_run1 = df_run1['framewise_displacement'].mean()
mean_fd_run2 = df_run2['framewise_displacement'].mean()

# get json info
j_file = f'{deriv_path}/{subject}_ses-{ses}_task-{task}_beh-descr.json'
with open(j_file, 'r') as file:
    data = json.load(file)
run1_accuracy = data['Run 1']['Overall Accuracy']
run1_mean_rt = data['Run 1']['Mean RT']
run2_accuracy = data['Run 2']['Overall Accuracy']
run2_mean_rt = data['Run 2']['Mean RT']


# Append the results to the DataFrame
result_df = pd.DataFrame({
    'Subject': [subject],
    'Session': [ses],
    'mFD_run1': [mean_fd_run1],
    'mFD_run2': [mean_fd_run2],
    'acc_run1': [run1_accuracy],
    'acc_run2': [run2_accuracy],
    'mrt_run1': [run1_mean_rt],
    'mrt_run2': [run2_mean_rt]
    })

existing_df = pd.concat([existing_df, result_df], ignore_index=True)
existing_df.to_csv(f'{deriv_path}/task-{task}_summ-mot-acc-rt.csv',index = False)
