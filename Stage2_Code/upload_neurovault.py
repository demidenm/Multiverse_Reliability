import argparse
import os
from pynv import Client
import pandas as pd


class NewClient(Client):
    def update_image(self, image_id, file, **data):
        files = {'file': open(file, 'rb')}
        return self.request(
            'patch',
            f'images/{image_id}',
            data=data,
            files=files
        ).json()
    def delete_image(self, image_id):
        return self.request(
            'delete',
            f'images/{image_id}'
        )


def del_collection_images(collection_number: int, est_type: list = None,
                          offset_start: int = 0, limit_batch: int = 10):
    """
    Fetches images from a collection, optionally filters by estimate types,
    and deletes them using provided API methods.

    Args:
        collection_number (int): Identifier for the collection of images.
        est_type (list, optional): List of estimate types to filter the images.
                                   Defaults to None (no filtering).
        offset_start (int, optional): Starting offset for fetching images in batches.
                                      Defaults to 0.
        limit_batch (int, optional): Number of images to fetch per batch.
                                     Defaults to 10.

    Returns:
        tuple: A tuple containing two DataFrames:
            - dat_full (pd.DataFrame): DataFrame containing all fetched images & associated details.
            - dat_sub (pd.DataFrame): DataFrame containing filtered images filted by est_type (if none, same as dat_full.
    """
    collection = collection_number
    offset = offset_start
    limit = limit_batch
    dat_full = pd.DataFrame()
    while True:
        try:
            i = api.get_collection_images(collection_id=collection, limit=limit, offset=offset)
            # Convert the current batch of results to a DataFrame & concatenate with previous
            batch_df = pd.DataFrame(i['results'])
            dat_full = pd.concat([dat_full, batch_df], ignore_index=True)
            # Update the offset for the next batch (running in batches of limit_batch)
            offset += limit
            # Check if all images have been fetched
            if offset >= i['count']:
                break  # Exit the loop if all images fetched
        except Exception as e:
            print(f"Error fetching images: {e}")
            break
    dat_sub = dat_full.copy()
    if est_type is not None:
        dat_sub = dat_sub[dat_sub['estimate_type'].isin(est_type)]
    for img_id in dat_sub['id']:
        try:
            api.delete_image(image_id=img_id)
        except Exception as e:
            print(f"Error for {img_id}: {e}")
    return dat_full, dat_sub

parser = argparse.ArgumentParser(description="Script to upload image maps to NeuroVault")

parser.add_argument("--token", help="File with NeuroVault Token Information")
parser.add_argument("--sample", help="Name of sample, AHRB, ABCD or MLS")
parser.add_argument("--group_files", help="list of image paths to group files")
parser.add_argument("--icc_files", help="lost of image paths to icc files")
parser.add_argument("--subsample_files", help="lost of image paths to icc files",
                    default=None)
parser.add_argument("--new_coll", help="Whether to create new collection",
                    default=None)
parser.add_argument("--coll_id", help="ID collection",
                    default=None)

args = parser.parse_args()

nv_token = args.token
sample = args.sample
grp_paths = args.group_files
icc_paths = args.icc_files
subsample_paths = args.subsample_files
create_coll = args.new_coll

# cog atlsa monetary incentive delay task
task = 'trm_4f23fc8c42d28'
task_name = 'monetary incentive delay task'

# Run code
with open(nv_token, 'r') as file:
    # get token info
    token_info = file.read()

api = Client(token_info.strip())

if create_coll is not None:
    collection_name = api.create_collection(f'{sample}: MNI152 3D maps for Multiverse Reliability')
    collection_id = collection_name['id']
else:
    collection_id = args.coll_id

# add group images
with open(grp_paths, 'r') as file:
    est_type = 'Group'
    est = 'cohens_d'
    for img_path in file:
        clean_path = img_path.strip()
        img_basename = os.path.basename(clean_path)
        file_details = img_basename.split('_')
        subs = None
        # Loop through each part of the path
        for part in file_details:
            if part.startswith('subs-'):
                subs = part.split('-')[1]
        image_name = f'{est_type}: {img_basename}'
        image = api.add_image(collection_id, clean_path, name=image_name, map_type='Other',
                              modality='fMRI-BOLD', analysis='G', sample_size={subs},
                              target_template_image='GenericMNI', type_design='event_related',
                              cognitive_paradigm_cogatlas=task, task_paradigm=task_name, estimate_type=est)

# Add ICC images
with open(icc_paths, 'r') as file:
    est_type = 'ICC'
    for img_path in file:
        clean_path = img_path.strip()
        img_basename = os.path.basename(clean_path)
        file_details = img_basename.split('_')
        subs = None
        stat = None
        # Loop through each part of the path
        for part in file_details:
            if part.startswith('subs-'):
                subs = part.split('-')[1]
            if part.startswith('stat-'):
                stat = part.split('-')[1]
            image_name = f'{est_type}: {img_basename}'
        image = api.add_image(collection_id, clean_path, name=image_name, map_type='Other',
                              modality='fMRI-BOLD', analysis='G', sample_size={subs},
                              target_template_image='GenericMNI', type_design='event_related',
                              cognitive_paradigm_cogatlas=task, task_paradigm=task_name, estimate_type=stat)

if subsample_paths is not None:
    with open(subsample_paths, 'r') as file:
        est_type = 'SubsampleICC'
        for img_path in file:
            clean_path = img_path.strip()
            img_basename = os.path.basename(clean_path)
            file_details = img_basename.split('_')
            subs = None
            stat = None
            # Loop through each part of the path
            for part in file_details:
                if part.startswith('subs-'):
                    subs = part.split('-')[1]
                if part.startswith('stat-'):
                    stat = part.split('-')[1]
                image_name = f'{est_type}: {img_basename}'
            image = api.add_image(collection_id, clean_path, name=image_name, map_type='Other',
                                  modality='fMRI-BOLD', analysis='G', sample_size={subs},
                                  target_template_image='GenericMNI', type_design='event_related',
                                  cognitive_paradigm_cogatlas=task, task_paradigm=task_name, estimate_type=stat)

