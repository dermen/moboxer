#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# set -e

# The first argument is the directory containing the twoconf PDBs
input_dir=$1

# The second argument is the path to the MTZ file
mtz_file=$2

# The third argument is the path to the EFF file
eff_file=$3

# Get MPI rank and size
rank=${OMPI_COMM_WORLD_RANK}
size=${OMPI_COMM_WORLD_SIZE}

# Create a dedicated logs directory for this step
mkdir -p "$input_dir/logs"
log_file="$input_dir/logs/rank${rank}_phenix.log"

count=0
for f in `find "${input_dir}" -name "twoconf*pdb"`
do

    # Distribute files based on the counter
    if [[ $((count % size)) -eq $rank ]]; then
        echo "Rank $rank: Refining file $f"

        PHENIX_CMD="phenix.refine \
            ${mtz_file} \
            ${f} \
            ${eff_file} \
            pdb_interpretation.clash_guard.nonbonded_distance_threshold=None \
            overwrite=true \
            main.number_of_macro_cycles=5"

        # Execute the command and pipe output to the log file
        $PHENIX_CMD >> "$log_file" 2>&1
    fi
done

echo "Rank $rank finished refining its assigned models."
