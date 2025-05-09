from Bio.PDB import PDBParser

def load_structure(pdb_file):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("native", pdb_file)
    residues = [res for res in structure.get_residues() if res.id[0] == " "]
    return residues

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

# --- Main ---
pdb_file = "1ahs.pdb"
l5_file = "../results/1AHSC/1AHSC_output.hdf5.l5"

residues = load_structure(pdb_file)
native_contacts = extract_native_contacts(residues)
predicted_contacts = load_predictions(l5_file, top_n=2 * len(residues))
TP, FP, FN, precision, recall, f1 = compute_metrics(native_contacts, predicted_contacts)

print(f"✅ F1-score = {f1:.3f}")
print(f"   Precision = {precision:.3f}, Recall = {recall:.3f}")
print(f"   TP = {TP}, FP = {FP}, FN = {FN}")

