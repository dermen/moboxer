
import os
import requests


def download_files(urls, dest_dir):
    """
    Downloads files from a list of URLs to a specified destination directory.

    Args:
        urls (dict): A dictionary where keys are filenames and values are URLs.
        dest_dir (str): The destination directory to save the files.
    """
    # Loop through the dictionary and download each file
    for filename, url in urls.items():
        filepath = os.path.join(dest_dir, filename)
        try:
            print(f"Downloading {url} to {filepath}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")


def run_pymol_command(script_path, input_pdb, output_pdb):
    """
    Runs a PyMOL command using a subprocess.
    """
    command = ["pymol", "-cqr", script_path, "--", input_pdb, output_pdb]
    command = " ".join(command)
    print(command)
    os.system(command)


def create_phenix_refine_phil(refine_file):
    s="""
refinement {
  pdb_interpretation {
    reference_coordinate_restraints {
      enabled = True
      exclude_outliers = False
      selection = water
      sigma = 0.1
    }
  }
  refine {
    strategy = *individual_sites *individual_sites_real_space rigid_body \
               *individual_adp group_adp tls occupancies group_anomalous den
    occupancies {
      remove_selection = All
    }
  }
  main.bulk_solvent_and_scale = False
  bulk_solvent_and_scale {
    k_sol_b_sol_grid_search = False
    minimization_k_sol_b_sol = False
    minimization_b_cart = False
    fix_k_sol = 0.42
    fix_b_sol = 45.0
  }
}

"""
    with open(refine_file, "w") as o:
        o.write(s)
    print(f"Wrote {refine_file}")


def main():
    data_to_download = {
        "ground_truth_water.pdb": "https://bl831.als.lbl.gov/~jamesh/challenge/twoconf/ground_truth_water.pdb",
        "refme.mtz": "https://bl831.als.lbl.gov/~jamesh/challenge/twoconf/refme.mtz",
        "1aho.pdb": "https://files.rcsb.org/download/1aho.pdb",
    }
    this_dir = os.path.dirname(__file__)
    dest_dir = os.path.join(this_dir, "../../data")
    os.makedirs(dest_dir, exist_ok=True)
    print(dest_dir)

    # Run the download function
    download_files(data_to_download, dest_dir)

    # strip out alt conf and water from 1aho.pdb and save as a reference pdb for generating alt locs
    no_alt_script = os.path.join(this_dir, "../pymol/no_alt.py")
    input_pdb = os.path.join(dest_dir, "1aho.pdb")
    output_pdb = os.path.join(dest_dir, "ref_no_alt.pdb")

    run_pymol_command(no_alt_script, input_pdb, output_pdb)

    refine_phil_file = os.path.join(dest_dir, "phenix_settings.eff")
    create_phenix_refine_phil(refine_phil_file)

    # copy the scoring script
    scripts_to_download = {
        "untangle_score.csh": "https://bl831.als.lbl.gov/~jamesh/challenge/twoconf/untangle_score.csh"
    }
    script_dest = os.path.join(this_dir, "../../scripts/")
    download_files(scripts_to_download, script_dest)


if __name__ == "__main__":
    main()
