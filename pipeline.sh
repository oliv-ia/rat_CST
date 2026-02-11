#!bin/bash

export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4

SUBJECT=$1
ATLAS_DIR=$2
OUTPUT_PREFIX=$3



# Preprocessing scaling as scanner has a scaling error 
python ./scale.py $SUBJECT $OUTPUT_PREFIX"_scaled.nii.gz" 
fslswapdim $OUTPUT_PREFIX"_scaled.nii.gz" x y -z $OUTPUT_PREFIX"_scaled_reorientated.nii.gz"
#cp $OUTPUT_PREFIX"_scaled.nii.gz" $OUTPUT_PREFIX"_scaled_reorientated.nii.gz"
fslreorient2std $OUTPUT_PREFIX"_scaled_reorientated.nii.gz" $OUTPUT_PREFIX"_scaled_reorientated_std.nii.gz"
N4BiasFieldCorrection -d 3 -i $OUTPUT_PREFIX"_scaled_reorientated_std.nii.gz" -o $OUTPUT_PREFIX"_scaled_reorientated_std_n4.nii.gz"
# Brain extraction, also generates a binary brain mask
bet4animal $OUTPUT_PREFIX"_scaled_reorientated_std_n4.nii.gz" $OUTPUT_PREFIX"_scaled_reorientated_std_n4_brain.nii.gz" -z 5 -m
if [ ! -f $ATLAS_DIR/WHS_SD_rat_T2star_v1.01_bet.nii.gz ]; then
    echo "Atlas masked image not found, creating it now."
    bet4animal ${ATLAS_DIR}/WHS_SD_rat_T2star_v1.01.nii.gz ${ATLAS_DIR}/WHS_SD_rat_T2star_v1.01_bet.nii.gz -z 5 -m
fi
# Assigning names for clarity
SUBJECT_MASKED=$OUTPUT_PREFIX"_scaled_reorientated_std_n4_brain.nii.gz"
SUBJECT_MASK=$OUTPUT_PREFIX"_scaled_reorientated_std_n4_brain_mask.nii.gz"
ATLAS_MASKED=${ATLAS_DIR}/WHS_SD_rat_T2star_v1.01_bet.nii.gz
ATLAS_MASK=${ATLAS_DIR}/WHS_SD_rat_T2star_v1.01_bet_mask.nii.gz


echo ready to register


echo "Rigid and affine transforms to subject image."
#run this one 
antsRegistration \
  -d 3 \
  -o [${OUTPUT_PREFIX}reg_,${OUTPUT_PREFIX}reg_Warped.nii.gz] \
  --initial-moving-transform [${ATLAS_MASKED},${SUBJECT_MASKED},1] \
  -t Rigid[0.1] \
  -m MI[${ATLAS_MASK},${SUBJECT_MASKED},1,32] \
  -c [500x250x100,1e-6,10] \
  -s 3x2x1vox \
  -f 8x4x2 \
  -t Affine[0.1] \
  -m MI[${ATLAS_MASKED},${SUBJECT_MASKED},1,32] \
  -c [50x20x0,1e-6,10] \
  -s 3x2x1vox \
  -f 8x4x2

# now SyN registration 

echo "Starting non-linear SyN registration."
# lightweight SyN registration
antsRegistration \
  -d 3 \
  -o [${OUTPUT_PREFIX}syn_,${OUTPUT_PREFIX}syn_Warped.nii.gz] \
  --initial-moving-transform ${OUTPUT_PREFIX}reg_0GenericAffine.mat \
  -t SyN[0.1,2,1] \
  -m CC[${ATLAS_MASKED},${SUBJECT_MASKED},1,2] \
  -c [50x30,1e-6,10] \
  -f 6x3 \
  -s 2x1vox \
  -v 1 \
  --masks [${ATLAS_MASK},${SUBJECT_MASK}]

echo "SyN registration completed."
antsApplyTransforms \
  -d 3 \
  -i ${SUBJECT_MASKED} \
  -r ${ATLAS_MASKED} \
  -o ${OUTPUT_PREFIX}_final.nii.gz \
  -t ${OUTPUT_PREFIX}syn_1Warp.nii.gz \
  -t ${OUTPUT_PREFIX}syn_0GenericAffine.mat

