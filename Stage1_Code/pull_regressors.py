from pandas import read_csv, DataFrame
from glob import glob
import os


def regressors(confound_path: str, regressor_type: str = 'opt1') -> DataFrame:
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
