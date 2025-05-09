from Bio.PDB import PDBParser
import numpy as np

def load_structure(pdb_path):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_path)
    return list(structure.get_residues())

def distance_cb(res1, res2):
    try:
        atom1 = res1['CB']
    except KeyError:
        atom1 = res1['CA']  # pour Glycine
    try:
        atom2 = res2['CB']
    except KeyError:
        atom2 = res2['CA']
    return (atom1 - atom2)

def load_predictions(l5_file, top_n=None):
    contacts = []
    with open(l5_file) as f:
        for line in f:
            i, j, score = line.strip().split()
            contacts.append((int(i), int(j), float(score)))
    contacts.sort(key=lambda x: x[2], reverse=True)
    if top_n:
        return contacts[:top_n]
    return contacts

def evaluate_ppv(pdb_file, l5_file):
    residues = load_structure(pdb_file)
    contacts = load_predictions(l5_file, top_n=2 * len(residues))

    TP = 0
    for i, j, _ in contacts:
        if i >= len(residues) or j >= len(residues):
            continue
        try:
            dist = distance_cb(residues[i], residues[j])
            if dist <= 8.0:
                TP += 1
        except Exception:
            continue
    PPV = TP / len(contacts)
    print(f"✅ PPV = {PPV:.3f} ({TP}/{len(contacts)} bons contacts)")

# Lancer l'évaluation
evaluate_ppv("1ahs.pdb", "../results/1AHSC/1AHSC_output.hdf5.l5")

