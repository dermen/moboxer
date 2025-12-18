#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Arguments passed from the main script
output_dir=$1     # Main output directory
mtz_file=$2       # Path to MTZ file
eff_file=$3       # Path to EFF file
jiggle_script=$4
score_script=$5   # Path to untangle_score.csh
ref_pdb=$6       # Path to the single-conformer PDB (from no_alt.py)
pymol_add_conf=$7 # Path to add_conf.py
Ntrials=$8
pyjiggler=$9
pymol_add_water=${10}
water_pdb=${11}
tar_to_h5=${12}

# Get MPI rank and size
if [[ -n "${SLURM_PROCID}" ]]; then
  # Slurm environment
  rank=${SLURM_PROCID}
  size=${SLURM_NPROCS}
elif [[ -n "${OMPI_COMM_WORLD_RANK}" ]]; then
  # OpenMPI or other environments
  rank=${OMPI_COMM_WORLD_RANK}
  size=${OMPI_COMM_WORLD_SIZE}
else
  # Neither Slurm nor OpenMPI variables are defined
  rank=0
  size=1
  echo "Unable to determine process rank and size. Setting rank=0 and size=1 (no parallelization)"
  #exit 1
fi

echo "Starting full workflow for Rank $rank of $size."

# Create a temporary working directory for this rank
rank_dir="$output_dir/working_rank_${rank}"

logf=${output_dir}/worker_logs/${rank}.logs

count=0
for ((count=0; count<$Ntrials; count++)); do
    if [[ $((count % size)) -eq $rank ]]; then

        temp_working_dir="$rank_dir/trial$count"
        mkdir -p "$temp_working_dir/jiggled"
        mkdir -p "$temp_working_dir/twoconf"
        mkdir -p "$temp_working_dir/twoconf_solvated"
        mkdir -p "$temp_working_dir/refined"

        # jiggle the reference PDB
        jiggle_pdb="$temp_working_dir/jiggled/jiggle.${count}.pdb"
        python "$pyjiggler" ${jiggle_script} ${ref_pdb} ${jiggle_pdb}

        # Combine base and jiggled models into a two-conformer model
        two_conf_pdb="$temp_working_dir/twoconf/twoconf.$count.pdb"
        pymol -cqr "$pymol_add_conf" \
            -- "$ref_pdb" \
            "$jiggle_pdb" \
            "$two_conf_pdb" \

        # add the ground truth water :
        two_conf_solvated_pdb="$temp_working_dir/twoconf_solvated/twoconf_solvated.$count.pdb"
        pymol -cqr "$pymol_add_water" \
            -- "$two_conf_pdb" "$water_pdb" "$two_conf_solvated_pdb"

        ## Run PHENIX refine on the two-conformer model
        refine_prefix="$temp_working_dir/refined/phx_${count}"
        command_array=(
          phenix.refine \
          "$mtz_file" \
          "$two_conf_pdb" \
          "$eff_file" \
          pdb_interpretation.clash_guard.nonbonded_distance_threshold=None \
          overwrite=true \
          main.number_of_macro_cycles=2 \
          output.prefix=$refine_prefix
        )

        # show the phenix command:
        command_string=$(printf "%s " "${command_array[@]}")
        printf "%s\n" "$command_string"
    {
        echo "=========================================================="
        echo "START TIME: $(date)"
        echo "RANK: $rank"
        echo "----------------------------------------------------------"
        # Actually run the command:
        "${command_array[@]}"
    } >> ${logf} 2>&1
        #Score the refined model
        cd "$temp_working_dir/refined/"
        refined_pdb=$(basename ${refine_prefix})_001.pdb
        "$score_script" "$refined_pdb" \
            > "score_${count}_base.log" 2>&1
        cd -

        echo "Rank $rank: Archiving temp results and cleaning up..."
        archive_name="$rank_dir/trial${count}.tar.gz"
        tar -czf "$archive_name" -C "$rank_dir" "trial$count"
        rm -rf "$temp_working_dir"

    fi
done

# Archive all rank results and clean up
echo "Rank $rank: Archiving results and cleaning up..."
archive_name="$output_dir/results_rank_${rank}.tar.gz"
tar -czf "$archive_name" -C "$rank_dir" .
rm -rf "$rank_dir"

# Run the per-rank tar to hdf5
echo "Rank $rank: extracting training data to hdf5"
h5_name="$output_dir/train_rank_${rank}.hdf5"
pymol -cqr "$tar_to_h5" --  "$archive_name" "$h5_name"

echo "Rank $rank finished. Archive saved to $archive_name."
