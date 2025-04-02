#!/bin/bash

# Ensure both input and output filenames are provided
# if [ "$#" -ne 2 ]; then
#     echo "Usage: $0 <input_file> <output_file>"
#     exit 1
# fi

INPUT=$1
# OUTPUT=$2

# Extract the grid information
ncks -v lat,rlon,rlat,rlon,precip $INPUT /mnt/d/RACMO/grid.nc

# Add periodic boundaries to the longitude and rlon (assuming longitude is the first dimension in the curvilinear grid)
ncap2 -s 'lat=cat(lat(:,0:0,:), lat, lat(:,0:0,:))' /mnt/d/RACMO/grid.nc -O /mnt/d/RACMO/grid.nc
ncap2 -s 'lon=cat(lon(:,0:0,:), lon, lon(:,0:0,:))' /mnt/d/RACMO/grid.nc -O /mnt/d/RACMO/grid.nc
ncap2 -s 'rlat=cat(rlat(0:0), rlat, rlat(0:0))' /mnt/d/RACMO/grid.nc -O /mnt/d/RACMO/grid.nc
ncap2 -s 'rlon=cat(rlon(0:0), rlon, rlon(0:0))' /mnt/d/RACMO/grid.nc -O /mnt/d/RACMO/grid.nc
ncap2 -s 'precip=cat(precip(:,:,0:0,:), precip, precip(:,:,0:0,:))' /mnt/d/RACMO/grid.nc /mnt/d/RACMO/tmp_with_periodic.nc

# Repeat the operation for the main data variables, e.g., 'precip'
# You may need to add this for other variables you have

# Update the grid information in the data file
# ncks -A -v lon,lat,rlon /mnt/d/RACMO/grid.nc tmp_with_periodic.nc

# Rename the file to the desired output
# mv tmp_with_periodic.nc $OUTPUT

# Clean up
rm /mnt/d/RACMO/grid.nc
