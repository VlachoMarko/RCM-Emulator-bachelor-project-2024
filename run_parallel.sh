#!/bin/bash

# Define the number of groups (adjust as needed)
NUM_GROUPS=12
GROUP_SIZE=2

# Run process_files.sh for each group in parallel
for ((i = 1; i <= NUM_GROUPS; i++)); do
    ./process_files.sh $i $GROUP_SIZE &
done

# Wait for all instances to finish
wait

echo "All groups processed"
