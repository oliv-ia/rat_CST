This script registers T2 rat brains to an atlas. It scales the subject image and shuffles the dimensions to match the Waxholm space atlas and performs an N4BiasFieldCorrection. 
Brains are extracted using bet4animal, and the skull stripped images are used for registration. Both linear (rigid/affine) and nonlinear (SyN) registrations are applied using ANTs.
This script relies on the following tools:
  FSL
  ANTs (antsRegistration)
Ensure these are installed and available in your system $PATH.
Example usage
```
./pipeline.sh rat01.nii.gz atlas_mask.nii.gz atlas.nii.gz rat01_output
```
To install necessary packages, run 
```
pip install -e . 
```
from the project root.