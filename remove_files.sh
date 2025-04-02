#!/bin/bash

# Directory containing the .nc files
DIRECTORY="/mnt/d/RACMO/SSP85"

# Find and remove files that contain "1degree-greenland-area" in their name
find "$DIRECTORY" -type f -name "*1degree-greenland-area*" -exec rm -v {} \;

echo "All files containing '1degree-greenland-area' have been removed."