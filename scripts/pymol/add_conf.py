
import argparse
from pymol import cmd


def add_conformers(args):
    """
    Creates two-conformer models by combining a reference PDB with a series of
    jiggled PDBs. The crystallographic unit cell and space group are read from
    the reference PDB and applied to the combined models.
    """
    cmd.load(args.refPDB, "ref")
    a,b,c,al,be,ga,sg = cmd.get_symmetry("ref")
    cmd.create( "ref_prot", "ref and polymer.protein")
    cmd.create( "ref_solv", "ref and solvent")
    cmd.delete("ref")
    #rms = cmd.align( "ref_prot" , "single")
    #assert rms[0] < 0.05

    cmd.alter("ref_prot", "chain='A'")
    cmd.alter(f"ref_prot", "alt='A'")
    cmd.alter("ref_solv", "chain='S'")

    pdb_obj = f"pdbJiggled"
    cmd.load(args.jigglePDB, pdb_obj)
    #rms = cmd.align(pdb_obj, "ref_prot")
    cmd.set_symmetry(pdb_obj, a,b,c,al,be,ga, spacegroup=sg)
    cmd.create(pdb_obj, f"{pdb_obj} and polymer.protein")

    cmd.alter(pdb_obj, "chain='A'")
    cmd.alter(pdb_obj, "alt='B'")
    cmd.create(pdb_obj, f"{pdb_obj} or ref_prot or ref_solv")
    cmd.alter(f"{pdb_obj}", "q=0.5")
#
    cmd.save(args.twoConfPDB, pdb_obj)
    cmd.delete(pdb_obj)
    #


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Combines a reference PDB with multiple jiggled PDBs "
                    "into two-conformer models."
    )

    # Add required arguments for the script
    parser.add_argument(
        "refPDB",
        type=str,
        help="Path to the reference PDB file (e.g., the output of no_alt.py)."
    )
    parser.add_argument(
        "jigglePDB",
        type=str,
        help="Path to a jiggled PDB file."
    )
    parser.add_argument(
        "twoConfPDB",
        type=str,
        help="Path to the new PDB name for the combined two-conformer model."
    )

    pa = parser.parse_args()
    add_conformers(pa)
