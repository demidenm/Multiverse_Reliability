from nipype.interfaces.fsl import ImageStats
from nipype.interfaces.fsl import SUSAN
from nipype import Workflow, Node

def susan_fwhm(inpath_bold: str, inpath_mask: str, fwhm: int):
    """
    This is a function to run FSL's SUSAN smoothing method:
    https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/SUSAN
    This is a nonlintear filtering that preserves boundaries of voxels with similar insensity (e.g., GM, WM, CSF, etc)

    :param inpath_bold: path to BOLD .nii.gz image, string object
    :param inpath_mask: path to brain mask .nii.gz image, string object
    :param fwhm: smoothing kernel to be used
    :return: return smoothed image
    """

    #stats_node = Node(ImageStats(), name='stats_node')
    #stats_node.inputs.in_file = inpath_bold
    #stats_node.inputs.op_string = '-k %s -p 50' % inpath_mask

    # Create a workflow and add the ImageStats node to it
    #wf = Workflow(name='my_workflow')
    #wf.add_nodes([stats_node])

    # workflow to get median brightness
    #results = wf.run()
    #median_val = float(results.outputs.stats_node.out_stat)

    # median brightness
    stats = ImageStats()
    stats.inputs.in_file = inpath_bold
    # using method from fmriprep confounds.py line # 688
    stats.inputs.op_string = '-k %s -p 50'
    stats.inputs.mask_file = inpath_mask
    result_mask = stats.run()
    median_val = float(result_mask.outputs.out_stat)

    # running susan
    #susan_node = Node(SUSAN(), name='susan_node')
    #susan_node.inputs.in_file = inpath_bold
    #susan_node.inputs.brightness_threshold = float(0.75 * median_val)
    #susan_node.inputs.fwhm = fwhm

    # workflow w/ SUSAN node
    #wf = Workflow(name='my_workflow')
    #wf.add_nodes([susan_node])
    #results = wf.run()
    #output_image = results.outputs.susan_node.output_image

    smooth = SUSAN()
    smooth.inputs.in_file =
    smooth.inputs.fwhm = fwhm
    # using method from fmriprep confounds.py line # 728
    smooth.inputs.brightness_threshold = float(0.75*median_val)
    smooth.inputs.out_file = 'output.nii.gz'
    smooth.inputs.output_type = 'NIFTI_GZ'
    result_susan = smooth.run()

    return result_susan
