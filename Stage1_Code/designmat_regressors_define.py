from pandas import read_csv, DataFrame, concat
from numpy import arange
from nilearn.glm.first_level import make_first_level_design_matrix
from glob import glob
import os


def pull_regressors(confound_path: str, regressor_type: str = 'opt1') -> DataFrame:
    """
    This function is compatible with the *confounds_timeseries.tsv file exported by fMRIprep
    When calling this function, provide the path to the confounds file for each subject (and run) and select
    the type of confounds to pull (opt_1 to opt_5).
    The functions returns a pandas dataframe with the extract confounds.

    :param confound_path: path to the *counfounds_timeseries.tsv
    :param regressor_type: Confound option from list 'conf_opt1','conf_opt2','conf_opt3','conf_opt4'
        'opt1': cosine_00 to cosine_03
        'opt2': opt1 + tran x, y, z & rot x, y, z
        'opt3': opt2 + trans x, y, z and rot x, y, z derivatives
        'opt4': opt3 + a_comp_cor 0:7 (top 8 components)
        'opt5': opt4 + motion outliers in confounds file
    :return: list of confound regressors
    """
    if not os.path.exists(confound_path):
        raise ValueError("Confounds file path not found. Check if {} exists".format(confound_path))

    confound_df = glob(confound_path)[0]
    confound_df = read_csv(confound_df, sep='\t', na_values=['n/a']).fillna(0)

    # Setting up dictionary from which to pull confound list
    if regressor_type != 'opt5':
        confound_dict = {
            "opt1": ['cosine00', 'cosine01', 'cosine02', 'cosine03'],
            "opt2": ['cosine00', 'cosine01', 'cosine02', 'cosine03',
                      'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'],
            "opt3": ['cosine00', 'cosine01', 'cosine02', 'cosine03',
                      'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                      'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1',
                      'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1'],
            "opt4": ['cosine00', 'cosine01', 'cosine02', 'cosine03',
                      'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                      'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1',
                      'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1',
                      "a_comp_cor_00", "a_comp_cor_01", "a_comp_cor_02", "a_comp_cor_03", "a_comp_cor_04",
                      "a_comp_cor_05", "a_comp_cor_06", "a_comp_cor_07"]
        }

    else:
        confound_dict = {
            "opt1": ['cosine00', 'cosine01', 'cosine02', 'cosine03'],
            "opt2": ['cosine00', 'cosine01', 'cosine02', 'cosine03',
                      'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'],
            "opt3": ['cosine00', 'cosine01', 'cosine02', 'cosine03',
                      'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                      'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1',
                      'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1'],
            "opt4": ['cosine00', 'cosine01', 'cosine02', 'cosine03',
                      'trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z',
                      'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1',
                      'rot_x_derivative1', 'rot_y_derivative1', 'rot_z_derivative1',
                      "a_comp_cor_00", "a_comp_cor_01", "a_comp_cor_02", "a_comp_cor_03", "a_comp_cor_04",
                      "a_comp_cor_05", "a_comp_cor_06", "a_comp_cor_07"]
        }

        motion_outlier_columns = confound_df.filter(regex='motion_outlier')
        # append the motion outlier columns to in dict to opt3  as opt5
        confound_dict['opt5'] = confound_dict['opt4'] + list(motion_outlier_columns.columns)

    return DataFrame(confound_df[confound_dict[regressor_type]])

def create_design_mid(events_df: DataFrame, bold_tr: int, num_volumes: int,
               onset_label: str, duration_label: str,
               conf_regressors: DataFrame, hrf_model: str = 'glover',
               stc: bool = False) -> DataFrame:
    """
    Creates a design matrix for each run with 5 anticipation 10 feedback conditions and
    specified regressors, such as cosine, motion and/or acompcor from fmriprep confounds.tsv

    :param events_df: this is the pandas dataframe for the events for the MID task
    :param bold_tr: TR for the BOLD volume,
    :param num_volumes: volumes in the BOLD
    :param onset_label: label to be used as the "onset" for cues, label in events_df,
        e.g. "CUE_ONSET" or "FIXATION_ONSET"
    :param duration_label: label to be used as the "duration" for cues, label in events_df,
        e.g. "CUE_DURATION","ANTICIPATION_DURATION" or "FIXATION_DURATION"
    :param conf_regressors: dataframe of nuisance regressors from def(regressors)
    :param hrf_model: select hrf model for design matrix, default glover
    :param stc: whether slice time correction was done. To adjust the onsets/frame times in design matrix.
            Default False, alt True
    :return: returns a design matrix for each run with 5 anticipation,
            10 feedback, contant + cosine + additional regressors
    """

    # Adding to events_df the cue + fixation duration for anticipation duration of model
    events_df["ANTICIPATION_DURATION"] = events_df["CUE_DURATION"] + events_df["FIXATION_DURATION"]

    # concatinating the condition types, onsets & duration from events_df for specified inputs
    conditions = concat([events_df.loc[:, "TRIAL_TYPE"], events_df.loc[:, "TRIAL_RESULT"]],
                        ignore_index=True)
    onsets = concat([events_df.loc[:, onset_label], events_df.loc[:, "FEEDBACK_ONSET"]],
                    ignore_index=True)
    duration = concat([events_df.loc[:, duration_label], events_df.loc[:, "FEEDBACK_DURATION"]],
                      ignore_index=True)

    # create pandas df with events
    design_events = DataFrame({'trial_type': conditions,
                               'onset': onsets,
                               'duration': duration})

    # Using the BOLD tr and volumes to generate the frame_times: acquisition time in seconds
    frame_times = arange(num_volumes) * bold_tr

    design_matrix_mid = make_first_level_design_matrix(
        # default modulation == '1'. Offset the times due to slice time correction, see blog post:
        # https://reproducibility.stanford.edu/slice-timing-correction-in-fmriprep-and-linear-modeling /
        frame_times=frame_times+(bold_tr/2) if stc else frame_times,
        events=design_events,
        hrf_model=hrf_model, drift_model=None, add_regs=conf_regressors
        )

    return design_matrix_mid
