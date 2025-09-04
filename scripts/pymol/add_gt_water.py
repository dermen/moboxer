import sys
import os
from pymol import cmd

# Check for the correct number of command-line arguments
if len(sys.argv) < 4:
    print("Usage: pymol -cqr add_gt_water.py -- <input_pdb> <water_pdb> <output_pdb>")
    sys.exit(1)

input_pdb = sys.argv[1]
water_pdb = sys.argv[2]
output_pdb = sys.argv[3]

# Load the input PDB file
cmd.load(input_pdb, "prot")

cmd.load(water_pdb, "water")
cmd.alter("water", "chain='S'")

# Select and remove alternate conformations
cmd.create("prot_or_water", "prot or water")

# Save the modified structure
cmd.save(output_pdb, "prot_or_water")

print(f"Added water from {water_pdb} to {input_pdb} and saved to {output_pdb}")
