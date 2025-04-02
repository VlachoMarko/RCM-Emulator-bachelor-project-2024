#!/bin/bash

# List of files with 20075 time steps
infiles=(
    "/mnt/d/RACMO/HIST/u0700-fullcombined-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/u0850-fullcombined-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0300-fullcombined-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0700-fullcombined-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0850-fullcombined-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/z0300-fullcombined-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
)

interfiles=(
    "/mnt/d/RACMO/HIST/u0700-interpcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/u0850-interpcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0300-interpcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0700-interpcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0850-interpcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/z0300-interpcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
)

selfiles=(
    "/mnt/d/RACMO/HIST/u0700-selcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/u0850-selcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0300-selcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0700-selcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0850-selcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/z0300-selcombined-greenland-area.KNMI-1950-2011.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
)


outfiles=(
    "/mnt/d/RACMO/HIST/u0700-fullcombined2-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/u0850-fullcombined2-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0300-fullcombined2-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0700-fullcombined2-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/v0850-fullcombined2-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
    "/mnt/d/RACMO/HIST/z0300-fullcombined2-greenland-area.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
)


# Loop through the list of files
for ((i = 0; i < ${#infiles[@]}; i++)); do
    # Interpolate time between 1980 and 1990
    infile="${infiles[i]}"
    interpolated_file="${interfiles[i]}"
    echo "Interpolating file: ${interfiles[i]}"
    cdo inttime,1989-01-01,00:00:00,1day $infile $interpolated_file

    # Select the time range
    selfile="${selfiles[i]}"
    cdo seldate,1990-12-31 $interpolated_file $selfile

    # Merge interpolated file with original file
    outfile="${outfiles[i]}"
    echo "Merging files: ${outfiles[i]}"
    cdo mergetime $infile $selfile $outfile
    
    # Remove the interpolated file
    rm "$interpolated_file"
done

