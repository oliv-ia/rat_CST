#!bin/bash
dir=$1
atlas_dir=$2
output_dir=$3


for subject in ${dir}/*.nii; do
    #get rid of spaces in filename
    new_subjectname=$(echo $subject | sed -r 's/[[:blank:]]+/_/g')
    mv "$subject" "$new_subjectname"
    
    filename=$(basename -- "$new_subjectname" ".nii")
    
    # define subject folder in output directory
    output_subfolder="${output_dir}/${filename}"
    mkdir -p "$output_subfolder"
    output_prefix="${output_subfolder}/${filename}"
    
    bash pipeline.sh "$new_subjectname" "$atlas_dir" "$output_prefix"
done