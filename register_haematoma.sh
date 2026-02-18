#!bin/bash
SUBJECT_HAEM=$1
ATLAS_DIR=$2
OUTPUT_PREFIX=$3


ATLAS_MASKED=${ATLAS_DIR}/WHS_SD_rat_T2star_v1.01_bet.nii.gz


# Preprocessing scaling as scanner has a scaling error 
python ./scale.py $SUBJECT_HAEM $OUTPUT_PREFIX"_haematoma_scaled.nii.gz" 
fslswapdim $OUTPUT_PREFIX"_haematoma_scaled.nii.gz" x y -z $OUTPUT_PREFIX"_haematoma_scaled_reorientated.nii.gz"
#cp $OUTPUT_PREFIX"_scaled.nii.gz" $OUTPUT_PREFIX"_scaled_reorientated.nii.gz"
fslreorient2std $OUTPUT_PREFIX"_haematoma_scaled_reorientated.nii.gz" $OUTPUT_PREFIX"_haematoma_scaled_reorientated_std.nii.gz"

antsApplyTransforms \
  -d 3 \
  -i $OUTPUT_PREFIX"_haematoma_scaled_reorientated_std.nii.gz" \
  -r ${ATLAS_MASKED} \
  -o ${OUTPUT_PREFIX}_haematoma_final.nii.gz \
  -t ${OUTPUT_PREFIX}syn_1Warp.nii.gz \
  -t ${OUTPUT_PREFIX}syn_0GenericAffine.mat

fslmaths ${OUTPUT_PREFIX}_haematoma_final.nii.gz -bin ${OUTPUT_PREFIX}_haematoma_final_bin.nii.gz
