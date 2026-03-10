import nibabel as nib
import numpy as np
import os
from scipy.spatial import cKDTree
from scipy.ndimage import binary_erosion
import pandas as pd

def calculate_overlap(atlas_path, nifti_path, cst_value):
    # Load images
    atlas_img = nib.load(atlas_path)
    img = nib.load(nifti_path)
    
    # Get binary data
    atlas_data = atlas_img.get_fdata()
    cst_mask = (atlas_data == cst_value).astype(np.uint8)
    data = img.get_fdata() > 0

    # Count raw voxel overlap
    volume_intersect = (cst_mask & data).sum()

    # Compute atlas voxel volume (mm³)
    voxel_volume_mm3 = abs(np.linalg.det(atlas_img.affine[:3, :3]))

    # Convert voxel overlap → mm³
    overlap_mm3 = volume_intersect * voxel_volume_mm3

    # Return voxel count + mm³
    return volume_intersect, overlap_mm3


def extract_surface(mask):
    # Extract surface voxels 
    eroded = binary_erosion(mask)
    surface = mask ^ eroded  # XOR = surface voxels only
    return np.argwhere(surface)


def compute_shortest_distance(atlas_path, nifti_path, cst_value):
    # Load images
    atlas_img = nib.load(atlas_path)
    img = nib.load(nifti_path)
    
    # Binary data
    atlas_data = atlas_img.get_fdata()
    cst_mask = (atlas_data == cst_value).astype(np.uint8)
    data = img.get_fdata() > 0
    
    # Extract surface voxel coordinates
    surface1 = extract_surface(cst_mask)
    surface2 = extract_surface(data)

    # If either structure has no surface voxels → infinite distance
    if surface1.size == 0 or surface2.size == 0:
        return float("inf")
    
    # Convert voxel indices → real‑world coordinates (mm)
    surface1_mm = nib.affines.apply_affine(atlas_img.affine, surface1)
    surface2_mm = nib.affines.apply_affine(img.affine, surface2)
    
    # KD-tree nearest surface distance
    tree = cKDTree(surface2_mm)
    distances, _ = tree.query(surface1_mm)

    return np.min(distances)


if __name__ == "__main__":
    print("check")
    
    ids = []
    counter = 0
    min_distances = []
    overlaps_vox = []
    overlaps_mm3 = []
    overlaps_binary = []
    
    registration_dir = "/Users/laurenhiggins/Library/CloudStorage/OneDrive-TheUniversityofManchester/CST_outputs/Faye_CST_outputs/T2_scans_6days"
    atlas_path = "/Users/laurenhiggins/Downloads/WHS_SD_rat_atlas_v4_pack/WHS_SD_rat_atlas_v4.nii.gz"
    cst_value = 1  # manually set for CST label


    for folder in os.listdir(registration_dir):
        if ".DS_Store" not in folder:
            filedir = os.path.join(registration_dir, folder)

            for file in os.listdir(filedir):
                if "haematoma_final_bin.nii.gz" in file:

                    id = str(folder)
                    haem_path = os.path.join(filedir, file)

                    # Get voxel and mm³ overlap
                    overlap_vox, overlap_mm3 = calculate_overlap(atlas_path, haem_path, cst_value)

                    # Binary CST overlap: 1 = any contact, 0 = none
                    overlap_bin = 1 if overlap_vox > 0 else 0

                    # Minimum distance (mm)
                    min_distance = compute_shortest_distance(atlas_path, haem_path, cst_value)

                    print(counter, " ID:", id,
                          "| Min distance:", min_distance,
                          "| Overlap:", overlap_bin,
                          "| Overlap voxels:", overlap_vox,
                          "| Overlap mm³:", overlap_mm3)

                    ids.append(id)
                    min_distances.append(min_distance)
                    overlaps_binary.append(overlap_bin)
                    overlaps_vox.append(overlap_vox)
                    overlaps_mm3.append(overlap_mm3)

                    counter += 1

    data = {
        "ID": ids,
        "Overlap": overlaps_binary,           
        "Overlap voxels": overlaps_vox,
        "Overlap volume mm3": overlaps_mm3,
        "Minimum distance": min_distances
    }

    print("Finished, processed", counter, "images.")

    df = pd.DataFrame(data)
    print(df)

    output_path = "/Users/laurenhiggins/Library/CloudStorage/OneDrive-TheUniversityofManchester/Stats/Faye_6d.xlsx"
    df.to_excel(output_path, index=False)