#!/bin/bash

# Directory containing the files
directory=/mnt/d/RACMO/HIST

# Check if directory exists
if [ ! -d "$directory" ]; then
    echo "Directory not found: $directory"
    exit 1
fi


mergefile="/mnt/d/RACMO/HIST/rh0500-1.4degree-fullgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
variable_str=""
merge_str=""

for file in "$directory"/*1.4degree-fullgreenland*; do
    if [ -f "$file" ]; then

        filename="$(basename "$file")"
        variable_str="${filename%%-*}"

        if [[   "$variable_str" == "rh0700" ||  "$variable_str" == "rh0850"  || "$variable_str" == "t0700"  || "$variable_str" == "t0850" 
                || "$variable_str" == "u0700" || "$variable_str" == "u0850" || "$variable_str" == "v0700" || "$variable_str" == "v0850" ||  "$variable_str" == "z0700" ]]; then
            
      
            echo "$variable_str"
            filename="$directory/$(basename "$file")"
            # merge_str="$merge_str $filename"

            echo "ncks -A -v $variable_str $filename $mergefile"




            # echo "Finished $file $(date +'%H:%M:%S')"
        fi
    fi
done

cdo showvar $mergefile
# echo "cdo mergetime $merge_str $mergefile"
# cdo mergetime $merge_str $mergefile


# echo "Processing $files_string"; cdo merge $files_string /mnt/d/RACMO/HIST/all-combined.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
