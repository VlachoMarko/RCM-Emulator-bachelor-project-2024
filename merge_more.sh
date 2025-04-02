#!/bin/bash

# Directory containing the .nc files
DIRECTORY="/mnt/d/RACMO/SSP85"

# Determine the group number from the parameter
GROUP_SIZE=5  # Adjust the group size as needed
END_SIZE=26
COUNTER=0
GROUP=$1
INPUT=$1

# Get the list of .nc files that contain "1degree" in their filenames
FILES=($(find "$DIRECTORY" -type f -name "*3degrees-nobnds-nopress*.nc"))

# Check if any files were found
if [ ${#FILES[@]} -eq 0 ]; then
    echo "No files found containing '1degree-nobnds' in their names."
    exit 1
fi

# Find all unique prefixes (the first two words separated by '-')
prefixes=($(printf "%s\n" "${FILES[@]}" | sed -n 's/^\(.*\/\)\{0,1\}\([^-]*-[^-]*\).*$/\2/p' | sort | uniq))
# echo "prefixes: $prefixes"

# Function to merge files for a given prefix
merge_files() {
    prefix=${prefixes[$(( GROUP-1 ))]}
    # prefix=$1
    
    echo "$prefix"

    local files=$(printf "%s\n" "${FILES[@]}" | grep "$prefix" | xargs)

    # Define the output filename
    local output_file="$DIRECTORY/${prefix}-nobnds-nopress-2011-2099.nc"

     if [[ "$prefix" != *"precip"* && "$prefix" != *"psurf"* && "$prefix" != *"v10m"* 
            && "$prefix" != *"u10m"* && "$prefix" != *"t2min"* && "$prefix" != *"t2m"* ]]; then
        # echo "Merging files for prefix: $prefix"


        # echo "cdo mergetime $files $output_file"
        cdo mergetime $files $output_file

        # echo "Finished processing --- $output_file --- at $(date +'%H:%M:%S') grp:$GROUP"
        COUNTER=$((COUNTER + 1))
          
        # Use cdo mergetime to merge the files
    fi
}

# Process files in parallel
process_group() {
    local start=$1
    local end=$2
    for ((i = start; i < end && i < ${#prefixes[@]}; i++)); do
        merge_files ${prefixes[$i]}
    done
}


# Determine the group number from the parameter

ARG1=$(( (INPUT - 1) * GROUP_SIZE))
ARG2=$((INPUT * GROUP_SIZE))
merge_files $ARG1 $ARG2
# process_group 0 $END_SIZE

echo "Total files processed: $COUNTER grp: $GROUP"
