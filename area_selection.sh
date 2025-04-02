#!/bin/bash

# Check if argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Directory containing the files
directory="$1"

# Check if directory exists
if [ ! -d "$directory" ]; then
    echo "Directory not found: $directory"
    exit 1
fi

for file in "$directory"/*-1combined-fullgreenland*; do
    if [ -f "$file" ]; then
        # Extract start and end of the file name
        filename=$(basename "$file")
        start="${filename%%.*}"
        end=".${filename#*.}"

        # Replace "-combined-fullgreenland" with "-southgreenland"
        start="${start//-1combined-fullgreenland/-southgreenland}"

        # Construct output file path
        outfile="/mnt/d/RACMO/HIST/${start}${end}"

        echo "Processing $file"
        echo "Output file: $outfile"

        # Perform concatenation
        cdo selindexbox,13,130,10,130 "$file" "$outfile"
    fi
done
