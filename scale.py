#!/usr/bin/env python3
import sys
import numpy as np
import nibabel as nib

fn_in = sys.argv[1]
fn_out = sys.argv[2]

img = nib.load(fn_in)
hdr = img.header.copy()
aff = img.affine.copy()

# factor to scale (here 10 -> we divide by 10)
factor = 10.0

# scale affine (affine maps voxel->mm so divide by factor to reduce world scale)
aff_new = aff.copy()
aff_new[:3, :3] = aff[:3, :3] / factor
aff_new[:3, 3] = aff[:3, 3] / factor

# update pixdim (pixdim[1:4] are x,y,z)
hdr['pixdim'][1] = hdr['pixdim'][1] / factor
hdr['pixdim'][2] = hdr['pixdim'][2] / factor
hdr['pixdim'][3] = hdr['pixdim'][3] / factor

# build new image with same data but corrected affine/header
new = nib.Nifti1Image(img.get_fdata(dtype=np.float32), aff_new, header=hdr)
nib.save(new, fn_out)
print("Wrote", fn_out)
