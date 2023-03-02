from pandas import DataFrame, concat
from numpy import arange
from nilearn.glm.first_level import make_first_level_design_matrix


def design_mid(events_df: DataFrame, bold_tr: int, num_volumes: int,
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
