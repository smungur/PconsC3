import os
import sys
import csv
import glob
import numpy as np
from Bio.PDB import PDBParser

# Parameters: minimum sequence separation and fraction of top contacts to evaluate
MIN_SEQ_SEP = 6      # ignore contacts with |i-j| < MIN_SEQ_SEP
TOP_FRACTION = 0.2   # default: use top L/5 contacts for evaluation


def load_predictions(pred_path):
    """Load predictions from a file as (i, j, score) tuples, ensuring i<j."""
    preds = []
    with open(pred_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue
            i, j, s = parts
            i, j = int(i), int(j)
            # enforce ordering i<j
            pi, pj = (i, j) if i < j else (j, i)
            preds.append((pi, pj, float(s)))
    return preds


def load_native_contacts(pdb_path, cutoff=8.0):
    """Extract native contacts (i,j) from PDB: CA distance <= cutoff and |i-j|>=MIN_SEQ_SEP."""
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('X', pdb_path)
    # flatten residues with CA
    residues = [res for model in structure for chain in model for res in chain
                if res.id[0]==' ' and 'CA' in res]
    n = len(residues)
    native = set()
    for a in range(n):
        for b in range(a + MIN_SEQ_SEP, n):
            dist = residues[a]['CA'] - residues[b]['CA']
            if dist <= cutoff:
                i = residues[a].id[1]
                j = residues[b].id[1]
                pi, pj = (i, j) if i < j else (j, i)
                native.add((pi, pj))
    return native


def evaluate_case(preds, native, L, fraction=TOP_FRACTION):
    """Filter by sequence sep, select top L*fraction, compute precision, recall, F1."""
    # filter
    filt = [(i,j,s) for (i,j,s) in preds if abs(i-j) >= MIN_SEQ_SEP]
    # sort
    sorted_preds = sorted(filt, key=lambda x: x[2], reverse=True)
    # select top
    top_n = max(1, int(L * fraction))
    top = sorted_preds[:top_n]
    pred_pairs = {(i,j) for (i,j,_) in top}
    # metrics
    TP = len(pred_pairs & native)
    FP = len(pred_pairs - native)
    FN = len(native - pred_pairs)
    prec = TP/(TP+FP) if (TP+FP)>0 else 0.0
    rec  = TP/(TP+FN) if (TP+FN)>0 else 0.0
    f1   = 2*prec*rec/(prec+rec) if (prec+rec)>0 else 0.0
    return prec, rec, f1


def main(input_dir):
    """Evaluate both 'results' and 'benchmarkset' predictions and write two CSV summaries."""
    # resolve project root
    base = os.path.basename(input_dir.rstrip(os.sep))
    if base in ('results', 'benchmarkset'):
        project_root = os.path.dirname(os.path.abspath(input_dir))
    else:
        project_root = input_dir
    results_dir = os.path.join(project_root, 'results')
    bench_dir   = os.path.join(project_root, 'benchmarkset')
    data_dir    = os.path.join(project_root, 'data')

    # check dirs
    for d in (results_dir, bench_dir, data_dir):
        if not os.path.isdir(d):
            print(f"Error: directory '{os.path.basename(d)}' missing under {project_root}")
            sys.exit(1)

    # load native contacts and length for each protein once
    native_map = {}
    length_map = {}
    for prot in os.listdir(data_dir):
        pdbs = glob.glob(os.path.join(data_dir, prot, '*.pdb'))
        if not pdbs:
            continue
        pdb_path = pdbs[0]
        native = load_native_contacts(pdb_path)
        structure = PDBParser(QUIET=True).get_structure('X', pdb_path)
        L = sum(1 for model in structure for chain in model for res in chain
                if res.id[0]==' ' and 'CA' in res)
        native_map[prot] = native
        length_map[prot] = L

    # evaluate results predictions
    results_summary = []
    for prot in os.listdir(results_dir):
        prot_dir = os.path.join(results_dir, prot)
        if not os.path.isdir(prot_dir) or prot not in native_map:
            continue
        l5s = glob.glob(os.path.join(prot_dir, '*_output.l5'))
        if not l5s: continue
        preds = load_predictions(l5s[0])
        prec, rec, f1 = evaluate_case(preds, native_map[prot], length_map[prot])
        results_summary.append((prot, prec, rec, f1))
    # write results_summary.csv
    out1 = os.path.join(project_root, 'results_summary.csv')
    with open(out1,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['Protein','Precision','Recall','F1'])
        for row in sorted(results_summary): w.writerow([row[0],f"{row[1]:.3f}",f"{row[2]:.3f}",f"{row[3]:.3f}"])
    print(f"Wrote {out1}")

    # evaluate benchmarkset layers
    bench_summary = []
    for prot in os.listdir(bench_dir):
        prot_dir = os.path.join(bench_dir, prot)
        if not os.path.isdir(prot_dir) or prot not in native_map:
            continue
        for layer in range(6):
            fname = f"pconsc3.l{layer}.out"
            path = os.path.join(prot_dir, fname)
            if not os.path.exists(path):
                print(f"Warning: missing {fname} for {prot}")
                continue
            preds = load_predictions(path)
            prec, rec, f1 = evaluate_case(preds, native_map[prot], length_map[prot])
            bench_summary.append((prot, layer, prec, rec, f1))
    # write benchmark_summary.csv
    out2 = os.path.join(project_root, 'benchmark_summary.csv')
    with open(out2,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['Protein','Layer','Precision','Recall','F1'])
        for prot,layer,prec,rec,f1 in sorted(bench_summary):
            w.writerow([prot,layer,f"{prec:.3f}",f"{rec:.3f}",f"{f1:.3f}"])
    print(f"Wrote {out2}")

if __name__=='__main__':
    if len(sys.argv)!=2:
        print("Usage: python evaluate_all_cases.py <project_root_or_results_or_benchmarkset_dir>")
        sys.exit(1)
    main(sys.argv[1])
