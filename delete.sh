#!/bin/bash

# Directory containing the .nc files
DIRECTORY="/mnt/d/RACMO/SSP85"

# Get the list of .nc files
FILES=($(find "$DIRECTORY" -type f -name "*2degrees.KNMI*.nc"))


FILEMAX=${#FILES[@]}
for ((i = 0; i < FILEMAX; i++)); do
    
    FILE=${FILES[$i]}
    BASENAME=$(basename "$FILE")
    variable_str="${BASENAME%%-*}"
    # echo "grp: $GROUP i: $i var: $variable_str"
    
    if [[ "$variable_str" != "precip" && "$variable_str" != "psurf" && "$variable_str" != "v10m" && "$variable_str" != "u10m" 
            && "$variable_str" != *"t2m"*  ]]; then
     
        echo "rm -v $FILE"
    fi

done
