from glob import glob
import argparse
from pyrelimri import similarity
warnings.filterwarnings("ignore")

# input arguments
parser = argparse.ArgumentParser(description="Script to run similarity estimate between func/anat masks")
parser.add_argument("--anat", help="path to anatomy MNI mask")
parser.add_argument("--func", help="path to func MNI mask")
parser.add_argument("--stype", help="similarity type, dice or jaccard")

# set variables and glob paths
args = parser.parse_args()
anat = args.anat
func = args.func
stype = args.stype
anat_path = glob(anat)
func_path = glob(func)

# run similarity
sim_est = similarity.image_similarity(imgfile1=anat_path,
                                      imgfile2=func_path,
                                      similarity_type=stype)
print(sim_est)



