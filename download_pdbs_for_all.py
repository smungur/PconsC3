#!/usr/bin/env python3
# This code was developed with the assistance of ChatGPT-4o (OpenAI)

import os
import requests

DATA_DIR = "data"

def download_pdb(pdb_id, output_path):
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_path, "w") as f:
            f.write(response.text)
        print(f"✅ Downloaded {pdb_id}.pdb to {output_path}")
    else:
        print(f"❌ Failed to download PDB for {pdb_id} (status code {response.status_code})")

def get_pdb_id_from_folder(folder_name):
    # Extract 4-letter PDB code from folder name (e.g., 1AHSC → 1AHS)
    return folder_name[:4].lower()

def main():
    for entry in os.listdir(DATA_DIR):
        full_path = os.path.join(DATA_DIR, entry)
        if os.path.isdir(full_path):
            pdb_id = get_pdb_id_from_folder(entry)
            pdb_file_path = os.path.join(full_path, f"{pdb_id}.pdb")
            if not os.path.exists(pdb_file_path):
                print(f"🔍 Downloading PDB for {pdb_id} into {entry}/")
                download_pdb(pdb_id, pdb_file_path)
            else:
                print(f"✅ {pdb_file_path} already exists")

if __name__ == "__main__":
    main()

