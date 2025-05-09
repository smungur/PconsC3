import os
from Bio.PDB import PDBParser

DATA_DIR = "data"
RESULTS_DIR = "results"
OUTPUT_FILE = "results_summary.csv"

def load_structure(pdb_file):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("native", pdb_file)
    return [res for res in structure.get_residues() if res.id[0] == " "]

def get_cb_distance(res1, res2):
    try:
        atom1 = res1['CB']
    except KeyError:
        atom1 = res1['CA']
    try:
        atom2 = res2['CB']
    except KeyError:
        atom2 = res2['CA']
    return atom1 - atom2

def extract_native_contacts(residues, max_dist=8.0, min_sep=5):
    native = set()
    for i in range(len(residues)):
        for j in range(i + min_sep, len(residues)):
            try:
                if get_cb_distance(residues[i], residues[j]) <= max_dist:
                    native.add((i, j))
            except:
                continue
    return native

def load_predictions(l5_file, top_n):
    preds = []
    with open(l5_file) as f:
        for line in f:
            i, j, score = line.strip().split()
            preds.append((int(i), int(j), float(score)))
    preds.sort(key=lambda x: x[2], reverse=True)
    return set((i, j) for i, j, _ in preds[:top_n])

def compute_metrics(native, predicted):
    TP = len(native & predicted)
    FP = len(predicted - native)
    FN = len(native - predicted)
    precision = TP / (TP + FP) if TP + FP > 0 else 0
    recall = TP / (TP + FN) if TP + FN > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
    return TP, FP, FN, precision, recall, f1

# Main loop
results = [("Protein", "TP", "FP", "FN", "Precision", "Recall", "F1-score")]
for protein_id in os.listdir(DATA_DIR):
    data_path = os.path.join(DATA_DIR, protein_id)
    result_path = os.path.join(RESULTS_DIR, protein_id)
    pdb_file = os.path.join(data_path, protein_id[:4].lower() + ".pdb")
    l5_file = os.path.join(result_path, protein_id + "_output.hdf5.l5")

    if not os.path.exists(pdb_file) or not os.path.exists(l5_file):
        print(f"⏭️ Skipping {protein_id} (missing files)")
        continue

    residues = load_structure(pdb_file)
    native_contacts = extract_native_contacts(residues)
    predicted_contacts = load_predictions(l5_file, top_n=2 * len(residues))
    TP, FP, FN, precision, recall, f1 = compute_metrics(native_contacts, predicted_contacts)

    print(f"✅ {protein_id}: F1 = {f1:.3f}, PPV = {precision:.3f}, Recall = {recall:.3f}")
    results.append((protein_id, TP, FP, FN, f"{precision:.3f}", f"{recall:.3f}", f"{f1:.3f}"))

# Save to CSV
with open(OUTPUT_FILE, "w") as f:
    for row in results:
        f.write(",".join(map(str, row)) + "\n")

print(f"\n📄 Summary saved to {OUTPUT_FILE}")

