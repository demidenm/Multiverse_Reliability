import argparse
import os
from pynv import Client

parser = argparse.ArgumentParser(description="Script to upload image maps to NeuroVault")

parser.add_argument("--token", help="File with NeuroVault Token Information")
parser.add_argument("--sample", help="Name of sample, AHRB, ABCD or MLS")
parser.add_argument("--file_path", help="list of image files")
parser.add_argument("--out_type", help="group or icc")
args = parser.parse_args()

nv_token = args.token
sample = args.sample
img_paths = args.file_path
est_type = args.out_type
task = 'monetary incentive delay task'

# Run code
with open(nv_token, 'r') as file:
    # get token info
    token_info = file.read()

api = Client(token_info.strip())
collection_name = api.create_collection(f'{sample}: 3D MNI152 maps for multiverse reliability')

with open(img_paths, 'r') as img_paths:
    for img_path in img_paths:
        clean_path = img_path.strip().replace('\n', '')
        img_basename = os.path.basename(clean_path)
        file_details = img_basename.split('_')
        subs = None
        # Loop through each part of the path
        for part in file_details:
            if part.startswith('subs-'):
                subs = part.split('-')[1]
        image_name = f'{est_type}: {img_basename}'
        image = api.add_image(collection_name['id'], img_path, name=image_name, map_type='Other',
                              modality='fMRI-BOLD', analysis='G', sample_size={subs},
                              target_template_image='GenericMNI', type_design='event_related',
                              cognitive_paradigm_cogatlas=task)
