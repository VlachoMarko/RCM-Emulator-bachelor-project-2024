#!/bin/bash

# Directory containing the .nc files
DIRECTORY="/mnt/d/RACMO/HIST"

# Get the list of .nc files
FILES=($(find "$DIRECTORY" -type f -name "*combined-fullgreenland*"))

# for ((i = 0; i < 250 && i < ${#FILES[@]}; i++)); do
#     FILE=${FILES[$i]}
#     echo "$FILE $i"
# done 

# Number of files per group
GROUP_SIZE=$2
END_SIZE=235
COUNTER=0
GROUP=1
# MERGE_STR="/mnt/d/RACMO/HIST/3degree-somevars-nobnds-nopress-fullgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"

# Function to process a group of files
process() {
  local start=$1
  local end=$2
  # MERGEFILE=${FILES[0]}

  FILEMAX=${#FILES[@]}

  for ((i = start; i < end && i < FILEMAX; i++)); do
    FILE=${FILES[$i]}
    BASENAME="$(basename "$FILE")"
    # MERGE_STR="$MERGE_STR $FILE"
    variable_str="${BASENAME%%-*}"
    
    if [[   "$variable_str" != "precip" && "$variable_str" != "psurf" && "$variable_str" != "v10m" 
            && "$variable_str" != "u10m" && "$variable_str" != *"t2m"* && "$variable_str" != "rh0300" ]]; then

        if [[    "$variable_str" == "rh0500" || "$variable_str" == "rh0700" ||  "$variable_str" == "rh0850"  || "$variable_str" == "t0700"  || "$variable_str" == "t0850" 
                || "$variable_str" == "u0700" || "$variable_str" == "u0850" || "$variable_str" == "v0700" || "$variable_str" == "v0850" ||  "$variable_str" == "z0700" ]]; then
            
            NEWNAME=$(echo "$BASENAME" | sed 's/combined-fullgreenland/1.4degree/')
            OUTFILE="${DIRECTORY}/${NEWNAME}"

            # echo "$variable_str"
            # echo "Processing --- $FILE --- at $(date +'%H:%M:%S') i:$i "

            cdo remapnn,1.4degree_grid.txt $FILE $OUTFILE
            # cdo showvar >> ncksm.txt $FILE
            
            FILE=$OUTFILE
            BASENAME=$(basename "$OUTFILE")
        
            NEWNAME=$(echo "$BASENAME" | sed 's/1.4degree/1.4degree-fullgreenland/')
            OUTFILE="${DIRECTORY}/${NEWNAME}"  
        

            cdo sellonlatbox,-74,-10,59,85 $FILE $OUTFILE
            rm -v $FILE

            FILE=$OUTFILE
            BASENAME=$(basename "$OUTFILE")
        
            NEWNAME=$(echo "$BASENAME" | sed 's/1.4degree/1.4degree-nobnds/')
            OUTFILE="${DIRECTORY}/${NEWNAME}"  

            ncwa -a bnds $FILE $OUTFILE
            rm -v $FILE

            FILE=$OUTFILE
            BASENAME=$(basename "$OUTFILE")
        
            NEWNAME=$(echo "$BASENAME" | sed 's/nobnds/nobnds-nopress/')
            OUTFILE="${DIRECTORY}/${NEWNAME}"  

            ncwa -a pressure $FILE $OUTFILE
            rm -v $FILE
            
            
            # echo "ncks -A -v $variable_str $OUTFILE $MERGE_STR"            
            # echo "Finished processing --- $OUTFILE --- at $(date +'%H:%M:%S') grp:$GROUP"
            COUNTER=$((COUNTER + 1))
        fi
    fi


  done
    
    # OUTFILE=$(echo "$FILE" | sed 's/2091/2015-2099/')
    # echo "cdo mergetime $MERGE_STR $OUTFILE"

}

# Determine the group number from the parameter
GROUP=$1
INPUT=$1

ARG1=$(( (INPUT - 1) * GROUP_SIZE))
ARG2=$((INPUT * GROUP_SIZE))
process $ARG1 $ARG2
# process 0 $END_SIZE

if [[ COUNTER -gt 0 ]]; then
    echo "Total files processed: $COUNTER grp: $GROUP"
fi



# #!/bin/bash

# # Directory containing the files
# directory="$1"

# # Check if directory exists
# if [ ! -d "$directory" ]; then
#     echo "Directory not found: $directory"
#     exit 1
# fi

# for file in "$directory"/*; do
#     if [ -f "$file" ]; then
#         echo "$file"
#         ncks -C -O -x -v dir,block1,block2,dtg,date_bnds,hms_bnds,assigned $file $file
#     fi
# done

# ncwa -a bnds /mnt/d/RACMO/HIST/precip-detailed-res-sgreenland.KNMI.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/precip-nobnds-detailed-res-sgreenland.KNMI.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
# ncwa -a height /mnt/d/RACMO/HIST/precip-nobnds-detailed-res-sgreenland.KNMI.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/precip-noheight-nobnds-detailed-res-sgreenland.KNMI.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
