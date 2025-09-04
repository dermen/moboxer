#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# set -e

# The first argument is the output directory
dirname=$1
mkdir -p ${dirname}

# Get the path to the jigglepdb.awk submodule
JIGGLE_AWK_SCRIPT="scripts/holton_scripts/fuzzymask/jigglepdb.awk"

# Input PDB file. This should be the output of your no_alt.py script.
# Make sure to pass this path from main_workflow.sh
input_pdb=$2

# Number of jiggled models to generate
njig=10240

# Get MPI rank and size
rank=${OMPI_COMM_WORLD_RANK}
size=${OMPI_COMM_WORLD_SIZE}

count=0
for i in $(seq 0 $((njig-1))); do
  if [[ $((count % size)) == $rank ]]; then

      # Generate random seed and shift value using Bash's built-in capabilities
      seed=$RANDOM
      # Generate a float between 1 and 2
      shift_val=$(awk -v min=1 -v max=2 'BEGIN{srand(); print min+rand()*(max-min)}')

      # Define the output path for the jiggled model
      jiggle_out="${dirname}/jiggle_${i}.pdb"

      # Run the jigglepdb.awk script directly
      # The -f flag specifies the AWK script file
      awk -f "$JIGGLE_AWK_SCRIPT" \
          -v shift=byB \
          -v seed="${seed}" \
          -v shift_scale="${shift_val}" \
          -v frac_thrubond=0.9 -v ncyc_thrubond=500 \
          -v frac_magnforce=1.1 -v ncyc_magnforce=500 \
          -v dry_shift_scale=1 \
          "${input_pdb}" > "${jiggle_out}"
  fi
  count=$((count+1))
done

echo "MPI rank $rank finished jiggling its assigned models."
