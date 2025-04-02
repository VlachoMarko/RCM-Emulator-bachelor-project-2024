#!/bin/bash

cdo remapnn,2degree_grid.txt /mnt/d/RACMO/HIST/updated-somevariables-southgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/2degree-remapnn-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
cdo sellonlatbox,-74,-10,59,85 /mnt/d/RACMO/HIST/2degree-remapnn-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/2degree-remapnn-somevariables-fullgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
rm /mnt/d/RACMO/HIST/2degree-remapnn-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc

cdo remapnn,3degree_grid.txt /mnt/d/RACMO/HIST/updated-somevariables-southgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/3degree-remapnn-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
cdo sellonlatbox,-74,-10,59,85 /mnt/d/RACMO/HIST/3degree-remapnn-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/3degree-remapnn-somevariables-fullgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
rm /mnt/d/RACMO/HIST/3degree-remapnn-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc

cdo remapbil,2degree_grid.txt /mnt/d/RACMO/HIST/updated-somevariables-southgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/2degree-remapbil-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
cdo sellonlatbox,-74,-10,59,85 /mnt/d/RACMO/HIST/2degree-remapbil-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/2degree-remapbil-somevariables-fullgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
rm /mnt/d/RACMO/HIST/2degree-remapbil-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc

cdo remapbil,3degree_grid.txt /mnt/d/RACMO/HIST/updated-somevariables-southgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/3degree-remapbil-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
cdo sellonlatbox,-74,-10,59,85 /mnt/d/RACMO/HIST/3degree-remapbil-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/3degree-remapbil-somevariables-fullgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
rm /mnt/d/RACMO/HIST/3degree-remapbil-somevariables-earth.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc


# Step 1: Rename height dimensions to a common name 'height'
# Extract multiple variables and overwrite original files
# echo "t2max processing"
# ncks -O -v t2max /mnt/d/RACMO/HIST/t2max-temp-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/t2max-temp-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
# echo "t2min processing"
# ncks -O -v t2min /mnt/d/RACMO/HIST/t2min-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/t2min-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
# echo "t2m processing"
# ncks -O -v t2m /mnt/d/RACMO/HIST/t2m-temp-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc /mnt/d/RACMO/HIST/t2m-temp-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc




# file1="/mnt/d/RACMO/HIST/t2max-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
# file2="/mnt/d/RACMO/HIST/t2min-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"
# file3="/mnt/d/RACMO/HIST/t2m-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc"

# ncks -A -v t2max $file1 $file3
# ncks -A -v t2min $file2 $file3

# # Merge the files
# cdo merge -remapbil,$file1 $file1 -remapbil,$file2 $file2 -remapbil,$file3 $file3 /mnt/d/RACMO/HIST/merged2-t2m-sgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc
