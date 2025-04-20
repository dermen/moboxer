from pymol import cmd
import h5py
import numpy as np


def get_res_ids_and_names(sel):
    res_info = []
    cmd.iterate(sel, lambda atom: res_info.append((int(atom.resi), atom.resn)))
    res_info = sorted(res_info, key=lambda x: x[0])
    return res_info


def load_conf(fname):
    cmd.load(fname, "prot")
    cmd.create("protA", "prot and alt A and name CA")
    cmd.create("protB", "prot and alt B and name CA")

    res_infoA = get_res_ids_and_names("protA")
    res_infoB = get_res_ids_and_names("protB")
    assert res_infoB== res_infoB

    res_ids, res_names= zip(*res_infoA)
    all_xyz_a = []
    all_xyz_b = []
    for idx in res_ids:
        xyz_a = cmd.get_coords(f"protA and resi {idx} and name CA", 1)
        xyz_b = cmd.get_coords(f"protB and resi {idx} and name CA", 1)
        #print(idx, xyz_a, xyz_b)
        all_xyz_a.append(xyz_a)
        all_xyz_b.append(xyz_b)
    all_xyz_ab = np.array( [all_xyz_a, all_xyz_b])[:,:,0]
    return all_xyz_ab


if __name__=="__main__":
    import glob
    import os
    fnames = glob.glob("/Users/dermen/untangle/all_piece_1/models/twoconf.*.pdb")
    all_xyz_ab = []
    all_scores = []
    for i_f, f in enumerate(fnames):
        xyz_ab = load_conf(f)
        all_xyz_ab.append(xyz_ab)
        score_f = f.replace("models/","").replace(".pdb", "_refine_001_score.txt")
        assert os.path.exists(score_f)
        score = float(open(score_f, 'r').readlines()[0].split()[0])
        all_scores.append(score)
        print(i_f, len(fnames), score)

    all_xyz_ab = np.array(all_xyz_ab)
    h = h5py.File("test_4d.hdf5", "w")
    h.create_dataset("data", data=all_xyz_ab)
    h.create_dataset("scores", data=all_scores)
    h.close()
