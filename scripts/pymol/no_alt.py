
import sys
from pymol import cmd

# Check for the correct number of command-line arguments
if len(sys.argv) < 3:
    print("Usage: pymol -cqr no_alt.py -- <input_pdb> <output_pdb>")
    sys.exit(1)

input_pdb = sys.argv[1]
output_pdb = sys.argv[2]

# Load the input PDB file
cmd.load(input_pdb, "prot")

# Select and remove alternate conformations
cmd.create("prot_no_alt", "prot and not alt B and not solvent")

# Save the modified structure
cmd.save(output_pdb, "prot_no_alt")

print(f"Removed alternate conformations from {input_pdb} and saved to {output_pdb}")
