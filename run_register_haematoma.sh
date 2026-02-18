#!bin/bash
dir=$1
atlas_dir=$2
output_dir=$3


for subject in ${dir}/*ipsi_haematoma.nii; do
    new_subjectname=$(echo $subject | sed -r 's/[[:blank:]]+/_/g')
    mv "$subject" "$new_subjectname"

    
    filename=$(basename -- "$new_subjectname" "_ipsi_haematoma.nii")
    echo applying haematoma registration for $filename
    # define subject folder in output directory
    output_subfolder="${output_dir}/${filename}"

    #if [[ ! -d "$output_subfolder" ]]; then
    #    echo "registration dir for ${filename} does not exist"
    #    exit 1
    #fi
    output_prefix="${output_subfolder}/${filename}"
    
    bash register_haematoma.sh "$subject" "$atlas_dir" "$output_prefix" 
done