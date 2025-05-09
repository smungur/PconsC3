from Bio.PDB import PDBParser
import numpy as np
import sys
import os

def compute_contact_map(pdb_file, distance_threshold=8.0, chain_id=None):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('protein', pdb_file)

    # Select first model
    model = structure[0]
    
    # Choose the specified chain, or first one
    chain = model[chain_id] if chain_id else list(model.get_chains())[0]

    # Get C-alpha atoms
    ca_atoms = [res['CA'] for res in chain if 'CA' in res and res.id[0] == ' ']
    n = len(ca_atoms)
    contact_map = np.zeros((n, n), dtype=int)

    # Compute contact map
    for i in range(n):
        for j in range(i + 1, n):
            dist = ca_atoms[i] - ca_atoms[j]
            if dist <= distance_threshold:
                contact_map[i, j] = 1
                contact_map[j, i] = 1

    return contact_map

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_contact_map.py structure.pdb [chain_id]")
        sys.exit(1)

    pdb_path = sys.argv[1]
    chain = sys.argv[2] if len(sys.argv) > 2 else None

    cmap = compute_contact_map(pdb_path, chain_id=chain)

    # Save as a simple text file
    output_path = os.path.splitext(pdb_path)[0] + ".contacts.txt"
    np.savetxt(output_path, cmap, fmt='%d')
    print(f"Contact map saved to: {output_path}")

