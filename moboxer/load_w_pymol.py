from pymol import cmd

fname="/Users/dermen/untangle/all_piece_1/models/twoconf.1.pdb"
cmd.load(fname, "prot")
cmd.create("protA", "prot and alt A")
cmd.create("protB", "prot and alt B")


def get_res_ids_and_names(sel):
    res_info = []
    cmd.iterate(sel, lambda atom: res_info.append((int(atom.resi), atom.resn)))
    res_info = list(set(res_info))
    return res_info

res_infoA = get_res_ids_and_names("protA")
res_infoB = get_res_ids_and_names("protB")
assert res_infoB== res_infoB

res_ids, resnames = zip(*res_infoA)
for idx in res_ids:
    com_a = cmd.centerofmass(f"protA and resi {idx}")
    com_b = cmd.centerofmass(f"protB and resi {idx}")
    print(com_a, com_b)

print("Done")
