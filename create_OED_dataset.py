import numpy as np
import nibabel as nib
import os

def remove_ventricles(atlas_path, nifti_path, vent_value):
    # Load images
    atlas_img = nib.load(atlas_path)
    img = nib.load(nifti_path)
    
    # Get binary data
    atlas_data = atlas_img.get_fdata()
    no_vent_mask = ~np.isin(atlas_data, vent_value)
    data = img.get_fdata()
    data_no_vent = data * no_vent_mask
    return data_no_vent

def flip_lesion(lesion_path):
    img = nib.load(lesion_path)
    lesion_data = img.get_fdata()
    flipped_data = np.flip(lesion_data, axis=0)
    return flipped_data, lesion_data

def split_ipsi_contra(data_no_vent, flipped_lesion_data, lesion_data):
    # Get mid point
    mid_point = lesion_data.shape[0] // 2 
    # SPlit lesion, flipped lesion and brian in half
    left_brain_data=np.zeros_like(data_no_vent)
    right_brain_data=np.zeros_like(data_no_vent)

    left_brain_data[:mid_point,:,:] = data_no_vent[:mid_point,:,:]
    right_brain_data[mid_point:,:,:] = data_no_vent[mid_point:,:,:]

    left_lesion_data=np.zeros_like(lesion_data)
    right_lesion_data=np.zeros_like(lesion_data)

    left_lesion_data[:mid_point,:,:] = lesion_data[:mid_point,:,:]
    right_lesion_data[mid_point:,:,:] = lesion_data[mid_point:,:,:]

    left_flipped_lesion_data=np.zeros_like(flipped_lesion_data)
    right_flipped_lesion_data=np.zeros_like(flipped_lesion_data)

    left_flipped_lesion_data[:mid_point,:,:] = flipped_lesion_data[:mid_point,:,:]
    right_flipped_lesion_data[mid_point:,:,:] = flipped_lesion_data[mid_point:,:,:]



    # identify which is conta and ipsi
    if left_lesion_data.sum() > right_lesion_data.sum():
        ipsi_lesion = left_lesion_data
        ipsi_brain = left_brain_data
        contra_lesion = right_flipped_lesion_data
        contra_brain = right_brain_data
    else:
        ipsi_lesion = right_lesion_data
        ipsi_brain = right_brain_data
        contra_lesion = left_flipped_lesion_data
        contra_brain = left_brain_data

    return ipsi_lesion, ipsi_brain, contra_lesion, contra_brain



if __name__ == "__main__":

    registration_dir = "/Users/user/Documents/postdoc/rat_CST/mary_d7_reg_test"
    atlas_path = "/Users/user/Downloads/WHS_SD_rat_atlas_v4_pack/WHS_SD_rat_atlas_v4.nii.gz"
    OED_dataset_path = "/Users/user/Documents/postdoc/rat_CST/OED_dataset"
    vent_value = [33, 125]


    for folder in os.listdir(registration_dir):
        id = str(folder)
        print("ID: ", id)
        if ".DS_Store" not in folder:
            filedir = os.path.join(registration_dir, folder)
            haem_file_name = id + "_haematoma_final_bin.nii.gz"
            haem_file_path = os.path.join(filedir, haem_file_name)
            brain_file_name = id + "_final.nii.gz"
            brain_file_path = os.path.join(filedir, brain_file_name)

            brain_img = nib.load(brain_file_path)

            brain_no_ventricles = remove_ventricles(atlas_path, brain_file_path, vent_value)
            flipped_lesion, lesion = flip_lesion(haem_file_path)
            ipsi_lesion, ipsi_brain, contra_lesion, contra_brain = split_ipsi_contra(brain_no_ventricles, flipped_lesion,lesion)

            save_path = OED_dataset_path + "/" + id

            ipsi_lesion_img = nib.Nifti1Image(ipsi_lesion, brain_img.affine)
            nib.save(ipsi_lesion_img, f'{save_path}_ipsi_lesion.nii.gz')
            ipsi_brain_img = nib.Nifti1Image(ipsi_brain, brain_img.affine)
            nib.save(ipsi_brain_img, f'{save_path}_ipsi_brain.nii.gz')
            contra_lesion_img = nib.Nifti1Image(contra_lesion, brain_img.affine)
            nib.save(contra_lesion_img, f'{save_path}_contra_lesion.nii.gz')
            contra_brain_img = nib.Nifti1Image(contra_brain, brain_img.affine)
            nib.save(contra_brain_img, f'{save_path}_contra_brain.nii.gz')


