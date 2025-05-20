import os
import sys
import csv
import glob
import numpy as np
from Bio.PDB import PDBParser

# Parameters: minimum sequence separation and fraction of top contacts to evaluate
MIN_SEQ_SEP = 6      # ignore contacts with |i-j| < MIN_SEQ_SEP
TOP_FRACTION = 0.5   # use top L/5 contacts by default


def load_predictions(l5_path):
    """Load predictions from a .l5 file as (i, j, score) tuples, ensuring i<j order."""
    preds = []
    with open(l5_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue  # skip malformed lines
            i, j, s = parts
            i, j = int(i), int(j)
            # enforce ordering
            pi, pj = (i, j) if i < j else (j, i)
            preds.append((pi, pj, float(s)))
    return preds


def load_native_contacts(pdb_path, cutoff=8.0):
    """Extract native contacts from a PDB file.

    Returns a set of (i, j) residue index pairs where C-alpha distance <= cutoff
    and sequence separation >= MIN_SEQ_SEP. Skips residues missing CA."""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('X', pdb_path)
    model = structure[0]

    # gather residues with CA atom in sequential order
    residues = []
    for chain in model:
        for res in chain:
            if res.id[0] == ' ' and 'CA' in res:
                residues.append(res)
    n = len(residues)

    native = set()
    for a in range(n):
        for b in range(a + MIN_SEQ_SEP, n):  # enforce minimum sequence separation
            ca1 = residues[a]['CA']
            ca2 = residues[b]['CA']
            dist = ca1 - ca2
            if dist <= cutoff:
                # use 1-based residue numbering from PDB
                i = residues[a].id[1]
                j = residues[b].id[1]
                native.add((i, j))
    return native


def evaluate_case(preds, native, L, fraction=TOP_FRACTION):
    """Filter, select top contacts, and compute precision, recall, F1 metrics."""
    # 1) filter by minimum sequence separation
    filtered = [(i, j, s) for (i, j, s) in preds if abs(i - j) >= MIN_SEQ_SEP]

    # 2) sort by descending score
    sorted_preds = sorted(filtered, key=lambda x: x[2], reverse=True)

    # 3) select top L * fraction
    top_n = max(1, int(L * fraction))
    top_preds = sorted_preds[:top_n]
    pred_pairs = {(i, j) for (i, j, _) in top_preds}

    # 4) compute metrics
    TP = len(pred_pairs & native)
    FP = len(pred_pairs - native)
    FN = len(native - pred_pairs)
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def main(input_dir):
    """Traverse results directory or treat input_dir as project root, evaluate each protein, and write summary CSV."""
    input_basename = os.path.basename(input_dir.rstrip(os.sep))
    if input_basename == 'results' and os.path.isdir(input_dir):
        project_root = os.path.dirname(os.path.abspath(input_dir))
    else:
        project_root = input_dir
    results_dir = os.path.join(project_root, 'results')
    data_dir = os.path.join(project_root, 'data')

    if not os.path.isdir(results_dir):
        print(f"Error: 'results' directory not found under {project_root}.")
        sys.exit(1)
    if not os.path.isdir(data_dir):
        print(f"Error: 'data' directory not found under {project_root}.")
        sys.exit(1)

    summary = []
    for protein in os.listdir(results_dir):
        prot_dir = os.path.join(results_dir, protein)
        if not os.path.isdir(prot_dir):
            continue

        l5_files = glob.glob(os.path.join(prot_dir, '*_output.l5'))
        if not l5_files:
            print(f"Warning: no .l5 file found for {protein}")
            continue
        l5_path = l5_files[0]
        preds = load_predictions(l5_path)

        pdb_files = glob.glob(os.path.join(data_dir, protein, '*.pdb'))
        if not pdb_files:
            print(f"Warning: no PDB file (.pdb) found in data/{protein}, skipping.")
            continue
        pdb_path = pdb_files[0]
        native = load_native_contacts(pdb_path)

        structure = PDBParser(QUIET=True).get_structure('X', pdb_path)
        L = sum(1 for chain in structure[0] for res in chain if res.id[0] == ' ' and 'CA' in res)

        prec, rec, f1 = evaluate_case(preds, native, L)
        summary.append((protein, prec, rec, f1))

    csv_path = os.path.join(project_root, 'results_summary.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Protein', 'Precision', 'Recall', 'F1'])
        for protein, prec, rec, f1 in summary:
            writer.writerow([protein, f"{prec:.3f}", f"{rec:.3f}", f"{f1:.3f}"])
    print(f"Summary written to {csv_path}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python evaluate_all_cases.py <results_folder_or_project_root>")
        sys.exit(1)
    main(sys.argv[1])
