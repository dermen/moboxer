#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define project-level variables
PROJECT_ROOT=$(pwd)

INPUT_MTZ="data/refme.mtz"
INPUT_EFF="data/phenix_settings.eff"
REF_PDB="data/ref_no_alt.pdb"
WATER_PDB="data/ground_truth_water.pdb"

OUTPUT_DIR="output/all_piece"
JIGGLE_AWK_SCRIPT="$PROJECT_ROOT/scripts/holton_scripts/fuzzymask/jigglepdb.awk"
JIGGLE_PY_SCRIPT="$PROJECT_ROOT/scripts/python/pyjiggler.py"
SCORING_SCRIPT="$PROJECT_ROOT/scripts/untangle_score.csh"
FULL_WORKER="$PROJECT_ROOT/scripts/bash/worker.sh"
PYMOL_ADD_CONF="$PROJECT_ROOT/scripts/pymol/add_conf.py"
PYMOL_ADD_WATER="$PROJECT_ROOT/scripts/pymol/add_gt_water.py"
TAR_TO_H5="$PROJECT_ROOT/scripts/pymol/tar_to_h5.py"
MPIRUN="mpirun -n 2"
ntrials=4

echo "Starting master workflow..."

mkdir -p "$OUTPUT_DIR"

echo "Launching full parallel workflow..."
$MPIRUN "$FULL_WORKER" \
    "$OUTPUT_DIR" \
    "$PROJECT_ROOT/$INPUT_MTZ" \
    "$PROJECT_ROOT/$INPUT_EFF" \
    "$JIGGLE_AWK_SCRIPT" \
    "$SCORING_SCRIPT" \
    "$REF_PDB" \
    "$PYMOL_ADD_CONF" \
    "$ntrials" \
    "$JIGGLE_PY_SCRIPT" \
    "$PYMOL_ADD_WATER" \
    "$WATER_PDB" \
    "$TAR_TO_H5"

echo "Full workflow complete. Results are in tarballs in the output directory."
