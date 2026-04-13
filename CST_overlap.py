import nibabel as nib
import numpy as np
import os
from scipy.spatial import cKDTree
from scipy.ndimage import binary_erosion
import pandas as pd
import sys

def calculate_overlap(atlas_path, nifti_path, cst_value):
    # Load images
    atlas_img = nib.load(atlas_path)
    img = nib.load(nifti_path)
    
    # Get binary data
    atlas_data = atlas_img.get_fdata()
    cst_mask = (atlas_data == cst_value).astype(np.uint8)
    data = img.get_fdata() > 0
    volume_intersect = (cst_mask & data).sum()
    if volume_intersect > 0:
        return 1, volume_intersect
    if volume_intersect == 0:
        return 0, 0
    else:
        return np.nan, np.nan

def calculate_interruption(atlas_path, nifti_path, cst_value):
    # Load images
    atlas_img = nib.load(atlas_path)
    img = nib.load(nifti_path)
    
    # Get binary data
    atlas_data = atlas_img.get_fdata()
    cst_mask = (atlas_data == cst_value).astype(np.uint8)
    data = img.get_fdata() > 0

    overlaps_L = []
    overlaps_R = []
    # Err if not the same length
    if len(data[1]) != len(cst_mask[1]):
        sys.exit("Length of haematoma seg not the same as length of the CST seg")
    # Iterate through the slices 
    for i in range(0, len(cst_mask[1])):

        cst_slice = cst_mask[:, i, :]
        haem_slice = data[:, i, :] 

        mid = cst_slice.shape[0] // 2

       
        cst_L = cst_slice[:mid, :]
        cst_R = cst_slice[mid:, :]

        haem_L = haem_slice[:mid, :]
        haem_R = haem_slice[mid:, :]

        # LEFT
        if cst_L.sum() == 0:
            overlap_L = 0
        else:
            area_intersect_L = (cst_L & haem_L).sum()
            overlap_L = (area_intersect_L / cst_L.sum()) * 100

        # RIGHT
        if cst_R.sum() == 0:
            overlap_R = 0
        else:
            area_intersect_R = (cst_R & haem_R).sum()
            overlap_R = (area_intersect_R / cst_R.sum()) * 100
        overlaps_L.append(overlap_L)
        overlaps_R.append(overlap_R)
            
    max_L = np.max(overlaps_L)
    max_R = np.max(overlaps_R)



    # Thresholding
    interrupted_L = 1 if max_L >= 90 else 0
    interrupted_R = 1 if max_R >= 90 else 0

    return max_L, interrupted_L, max_R, interrupted_R

    




def extract_surface(mask):
    # Extract surface voxels 
    eroded = binary_erosion(mask)
    surface = mask ^ eroded  # XOR to get surface voxels
    return np.argwhere(surface)

def compute_shortest_distance(atlas_path, nifti_path, cst_value):
 
    # Load images
    atlas_img = nib.load(atlas_path)
    img = nib.load(nifti_path)
    
    # Get binary data
    atlas_data = atlas_img.get_fdata()
    cst_mask = (atlas_data == cst_value).astype(np.uint8)

    data = img.get_fdata() > 0
    
    # Extract surface points in voxel space
    surface1 = extract_surface(cst_mask)
    surface2 = extract_surface(data)
    
    if len(surface1) == 0 or len(surface2) == 0:
        raise ValueError("One or both volumes have no surface voxels: ", nifti_path, "length atlas: ", len(surface1), "length haem: ", len(surface2))
    
    # Convert voxel coordinates to real-world coordinates using affine transformation
    surface1_mm = nib.affines.apply_affine(atlas_img.affine, surface1)
    surface2_mm = nib.affines.apply_affine(img.affine, surface2)
    
    # Compute nearest neighbor distances using KDTree
    tree = cKDTree(surface2_mm)
    distances, _ = tree.query(surface1_mm)
    
    return np.min(distances)


if __name__ == "__main__":
    
    ids = []
    counter = 0
    min_distances = []
    overlaps = []
    overlap_volumes = []
    max_overlaps_L = []
    max_overlaps_R = []
    tract_interrupt_L = []
    tract_interrupt_R = []
    registration_dir = "/Users/user/Documents/postdoc/rat_CST/mary_d7_reg_test"
    atlas_path = "/Users/user/Downloads/WHS_SD_rat_atlas_v4_pack/WHS_SD_rat_atlas_v4.nii.gz"
    cst_value = 1 


    for folder in os.listdir(registration_dir):
        if ".DS_Store" not in folder:
            filedir = os.path.join(registration_dir, folder)
            for file in os.listdir(filedir):
                if "haematoma_final_bin.nii.gz" in file:
                    id = str(folder)

                    haem_path = os.path.join(filedir, file)
                
                    overlap, overlap_vol = calculate_overlap(atlas_path, haem_path, cst_value)
                    max_overlap_L, interruption_L, max_overlap_R, interruption_R = calculate_interruption(atlas_path, haem_path, cst_value)
                    min_distance = compute_shortest_distance(atlas_path, haem_path, cst_value)
                    
                
                    print(counter, " ID: ", id, "Min distance: ",min_distance, "Overlap: ", overlap_vol)

                    
                    ids.append(id)
                    min_distances.append(min_distance)
                    overlaps.append(overlap)
                    overlap_volumes.append(overlap_vol)
                    max_overlaps_L.append(max_overlap_L)
                    max_overlaps_R.append(max_overlap_R)
                    tract_interrupt_L.append(interruption_L)
                    tract_interrupt_R.append(interruption_R)
                    counter += 1

    data = {"ID": ids,
            "Overlap": overlaps,
            "Overlap volume": overlap_volumes,
            "Minium distance": min_distances,
            "Max overlap L": max_overlaps_L,
            "Max overlap R": max_overlaps_R,
            "Tract interruption_L": tract_interrupt_L,
            "Tract interruption_R": tract_interrupt_R

            }
    print("Finished, processed ", counter, " images.")


    df = pd.DataFrame(data)
    print(df)
    df.to_excel("/Users/user/Documents/postdoc/rat_CST/rat_haematomas/cst_interactions.xlsx")
    
