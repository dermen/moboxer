# ==============================================================================
# This script consolidates data from multiple compressed tarball files,
# processes them using PyMOL, and stores the results in a single HDF5 file.
# This approach minimizes file count and inode usage.
# ==============================================================================
import re

import sys
import h5py
import numpy as np
import os
import tarfile
from pymol import cmd


# --- PyMOL helper functions (reused from your original script) ---
def get_res_ids_and_names(sel):
    res_info = []
    cmd.iterate(sel, lambda atom: res_info.append((int(atom.resi), atom.resn)))
    res_info = sorted(res_info, key=lambda x: x[0])
    return res_info


def load_conf(fname):
    """
    Loads a two-conformation PDB file from disk, extracts coordinates,
    and returns them as a numpy array.
    """
    cmd.read_pdbstr(fname, "prot")
    #cmd.load(fname, "prot")
    cmd.create("protA", "prot and alt A and name CA")
    cmd.create("protB", "prot and alt B and name CA")

    res_infoA = get_res_ids_and_names("protA")
    res_infoB = get_res_ids_and_names("protB")
    assert res_infoA == res_infoB

    res_ids, res_names = zip(*res_infoA)
    all_xyz_a = []
    all_xyz_b = []
    for idx in res_ids:
        xyz_a = cmd.get_coords(f"protA and resi {idx} and name CA", 1)
        xyz_b = cmd.get_coords(f"protB and resi {idx} and name CA", 1)
        all_xyz_a.append(xyz_a)
        all_xyz_b.append(xyz_b)

    all_xyz_ab = np.array([all_xyz_a, all_xyz_b])[:, :, 0]
    cmd.delete("all")

    return all_xyz_ab


if __name__ == "__main__":
    rank_tarball = sys.argv[1]
    outname = sys.argv[2]

    all_xyz_ab = []
    all_scores = []
    #os.makedirs(rank_tempdir, exist_ok=True)
    with tarfile.open(rank_tarball, "r:gz") as rank_tar:
        for rank_mem in rank_tar.getmembers():
            name = os.path.basename(rank_mem.name)
            if name.startswith(".") or not name.endswith(".tar.gz"):
                continue

            sub_tar_f = rank_tar.extractfile(rank_mem)
            with tarfile.open(fileobj=sub_tar_f, mode="r:gz") as trial_tar:
                # Find the PDB and score files within the tarball
                trial_fnames = {os.path.basename(m.name):m for m in trial_tar.getmembers()}
                pdb_member = [m for f, m in trial_fnames.items() if re.match("twoconf.[0-9]+.pdb", f) is not None]
                score_member = [m for f, m in trial_fnames.items() if re.match("phx_[0-9]+_001_score.txt", f) is not None]
                try:
                    assert len(pdb_member) == 1
                    assert len(score_member) ==1
                except AssertionError as e:
                    print("Failed to find expected pdb and score.txt files")
                    print(str(e))
                    continue

                #trial_tar.extract(pdb_member[0], path=rank_tempdir, filter="data")
                #pdb_path = os.path.join(rank_tempdir, pdb_member[0].name)
                #xyz_ab = load_conf(pdb_path)

                with trial_tar.extractfile(pdb_member[0]) as pdb_file:
                    pdb_str = pdb_file.read()
                    xyz_ab = load_conf(pdb_str)

                with trial_tar.extractfile(score_member[0]) as score_file:
                    score = float(score_file.readlines()[0].split()[0])

                all_xyz_ab.append(xyz_ab)
                all_scores.append(score)

                print(f"  -> Successfully processed. Score: {score}")

    all_xyz_ab = np.array(all_xyz_ab)

    # Save the consolidated data to a single HDF5 file
    try:
        with h5py.File(outname, "w") as hf:
            hf.create_dataset("data", data=all_xyz_ab)
            hf.create_dataset("scores", data=all_scores)
            print(f"\nSuccessfully created {outname}.hdf5.")
            print(f"Final data shape: {all_xyz_ab.shape}")
            print(f"Final scores count: {len(all_scores)}")
    except Exception as e:
        print(f"An error occurrGed while creating the HDF5 file: {e}")
