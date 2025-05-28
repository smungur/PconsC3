import os
import sys
import csv
import glob
import numpy as np
from Bio.PDB import PDBParser, PPBuilder
from Bio import SeqIO
from Bio.Align import PairwiseAligner
from Bio.Data.IUPACData import protein_letters_3to1 as _triple2single
from multiprocessing import Pool
import time

# Parameters: minimum sequence separation and fraction of top contacts to evaluate
MIN_SEQ_SEP = 5      # we follow |i-j| ≥ 5 as in the article
#TOP_FRACTION = 0.2   # default: use top L/5 contacts for evaluation

aligner = PairwiseAligner()
aligner.mode = "global"

# Helper: convert 3-letter code to 1-letter
def three_to_one(resname):
    return _triple2single.get(resname.capitalize(), 'X')

# Helper: build a mapping from your FASTA indices → PDB residue numbers
def build_seq2pdb(fasta_path, pdb_path):
    # 1) load your exact DCA sequence
    target = str(next(SeqIO.parse(fasta_path, 'fasta')).seq).replace('-', '')
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('X', pdb_path)[0]

    best_score = -1
    best_chain = None

    for chain in structure:
        # collect CA atoms for this chain
        residues = [r for r in chain if r.id[0]==' ' and 'CA' in r]
        if not residues:
            continue
        # build chain sequence
        chain_seq = ''.join(three_to_one(r.resname) for r in residues)
        if len(chain_seq) == 0:
            continue
        # try alignment, skip if none
        try:
            aln = aligner.align(target, chain_seq)[0]
        except IndexError:
            continue
        if aln.score > best_score:
            best_score = aln.score
            best_chain = (residues, aln)

    if best_chain is None:
        # fallback: naive enumeration
        print(f"WARNING: no good chain alignment for {os.path.basename(pdb_path)}, falling back to naive mapping")
        residues = [r for chain in structure for r in chain if r.id[0]==' ' and 'CA' in r]
        return { i+1: residues[i].id[1] for i in range(len(residues)) }

    residues, (t_aln, c_aln, *_ ) = best_chain
    # walk the alignment
    seq2pdb = {}
    t_idx = c_idx = 0
    for a_t, a_c in zip(t_aln, c_aln):
        if a_t != '-': t_idx += 1
        if a_c != '-': c_idx += 1
        if a_t != '-' and a_c != '-':
            seq2pdb[t_idx] = residues[c_idx-1].id[1]
    return seq2pdb



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
    """Extract native contacts using Cβ–Cβ ≤ cutoff, with Cα fallback for Glycine."""
    parser    = PDBParser(QUIET=True)
    structure = parser.get_structure('X', pdb_path)
    residues = []
    for model in structure:
        for chain in model:
            for res in chain:
                # only standard amino acids
                if res.id[0] != ' ':
                    continue
                # try CB, then CA; if neither present, skip residue
                if 'CB' in res:
                    atom = res['CB']
                elif 'CA' in res:
                    atom = res['CA']
                else:
                    # skip residues with no backbone atom
                    continue
                # record (residue_number, Atom)
                residues.append((res.id[1], atom))

    native = set()
    n = len(residues)
    for a in range(n):
        i, atom_i = residues[a]
        for b in range(a + MIN_SEQ_SEP, n):
            j, atom_j = residues[b]
            # compute distance
            if (atom_i - atom_j) <= cutoff:
                pi, pj = (i, j) if i < j else (j, i)
                native.add((pi, pj))
    return native

def parseStats(f):
    stats = []
    ff = open(f).readlines()
    if len(ff) != 6:
        sys.stderr.write(f + ' has incorrect format!\n')
        return [-1, -1, -1, -1, -1, -1]
    for l in ff:
        stats.append(float(l.split()[-1]))
    return stats


def compute_ppv_long(preds, native, sep=24, top_fraction=2.0, seq_length=None):
    cand = [(i,j,s) for (i,j,s) in preds if abs(i-j) >= sep]
    cand.sort(key=lambda x: x[2], reverse=True)
    if seq_length is None:
        L = max(max(i, j) for (i, j, _) in preds)
    else:
        L = seq_length
    N = int(top_fraction * L)
    top = cand[:N]
    tp = sum((i,j) in native for i,j,_ in top)
    fp = len(top) - tp
    return tp / (tp + fp) if tp + fp > 0 else 0.0

def evaluate_ppv(preds, native, top_fraction=2.0, seq_length=None):
    """
    preds         : list of (i, j, score)
    native        : set of (i, j) true contacts
    top_fraction  : float, multiply by L to get N
    seq_length    : int, length of the sequence (optional)
    returns       : ppv (float)
    """
    # 1) drop short‐range
    candidates = [(i,j,s) for i,j,s in preds if abs(i-j) >= MIN_SEQ_SEP]
    # 2) sort by score desc
    candidates.sort(key=lambda x: x[2], reverse=True)

    # 3) get L, the seq length
    if seq_length is None:
        # fallback: approximate L as the highest residue index seen
        L = max(max(i,j) for i,j,_ in preds)
    else:
        L = seq_length

    # 4) compute N = top_fraction × L
    N = int(top_fraction * L)

    # 5) take the top N
    top_preds = candidates[:N]
    pred_pairs = {(i,j) for i,j,_ in top_preds}

    # 6) compute TP & FP
    TP = len(pred_pairs & native)
    FP = len(pred_pairs - native)

    # 7) PPV
    ppv = TP / (TP + FP) if (TP + FP) else 0.0
    return ppv


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
    start_all = time.perf_counter()
    native_map = {}
    length_map = {}
    t0 = time.perf_counter()
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
    end_all = time.perf_counter()
    print(f"[Timing] Native‐contact loop: {end_all - t0:.1f}s over {len(native_map)} proteins")
    #print(f"[Timing] Total script up to here: {end_all - start_all:.1f}s")

    # evaluate results predictions
    # before any loops, after you load native_map & length_map…
    results_summary = []
    seq2pdb_map = {}
    stats_map = {}
    for prot in os.listdir(results_dir):
        prot_dir = os.path.join(results_dir, prot)
        if not os.path.isdir(prot_dir) or prot not in native_map:
            continue
        l5s = glob.glob(os.path.join(prot_dir, '*_output.l5'))
        if not l5s: continue
        from Bio import SeqIO
        
        st_file = os.path.join(data_dir, prot, 'alignment.stats')
        if os.path.exists(st_file):
            stats = parseStats(st_file)
            beff = stats[3]
            L = stats[0]
            #stats_map[prot] = beff

        # --- PRECOMPUTE mapping once ---
        fasta_path = os.path.join(data_dir, prot, 'sequence.fa')
        pdb_file   = glob.glob(os.path.join(data_dir, prot, '*.pdb'))[0]
        seq2pdb_map[prot]     = build_seq2pdb(fasta_path, pdb_file)
        
        # Load, remap & evaluate in one pass
#        l5s = glob.glob(os.path.join(prot_dir, '*_output.l5'))
#        if not l5s:
#            continue
        raw_preds = load_predictions(l5s[0])
        seq2pdb = seq2pdb_map[prot]
        preds = [
            (seq2pdb[i], seq2pdb[j], s)
            for i,j,s in raw_preds
            if i in seq2pdb and j in seq2pdb
        ]
       # ppv = evaluate_ppv(preds, native_map[prot])
       # L   = length_map[prot]
       # beff = stats_map.get(prot, None)
        ppv = evaluate_ppv(preds, native_map[prot], top_fraction=2.0, seq_length=L)
        ppv_lr = compute_ppv_long(preds, native_map[prot], top_fraction=2.0, seq_length=L)
        results_summary.append((prot, ppv, ppv_lr, beff, L))
    # write results_summary.csv
    out1 = os.path.join(project_root, 'results_summary.csv')
    with open(out1,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['Protein','PPV', 'PPV_long','Beff','Length'])
        for prot, ppv,ppv_lr, beff, L in sorted(results_summary):
            w.writerow([
                prot,
                f"{ppv:.3f}",
                f"{ppv_lr:.3f}",
                f"{beff:.1f}",
                 str(int(L)),
            ])
    print(f"Wrote {out1}")

    # evaluate benchmarkset layers
    bench_summary = []
    # before any loops, after you load native_map & length_map…
    seq2pdb_map = {}
    stats_map = {}
    for prot in os.listdir(bench_dir):
        prot_dir = os.path.join(bench_dir, prot)
        if not os.path.isdir(prot_dir) or prot not in native_map:
            continue
        st_file = os.path.join(data_dir, prot, 'alignment.stats')
        if os.path.exists(st_file):
            stats = parseStats(st_file)
            beff = stats[3]
            L = stats[0]
          #  stats_map[prot] = beff
        
        # --- PRECOMPUTE per-protein mapping and raw preds by layer ---
        fasta_path = os.path.join(data_dir, prot, 'sequence.fa')
        pdb_file   = glob.glob(os.path.join(data_dir, prot, '*.pdb'))[0]
        seq2pdb_map[prot]    = build_seq2pdb(fasta_path, pdb_file)
            
        # only layer 5 → record (prot,prec,rec,f1) without layer
        path5 = os.path.join(prot_dir, "pconsc3.l5.out")
        if os.path.exists(path5):
            raw_preds = load_predictions(path5)
            seq2pdb   = seq2pdb_map[prot]
            preds = [
                (seq2pdb[i], seq2pdb[j], s)
                for i, j, s in raw_preds
                if i in seq2pdb and j in seq2pdb
            ]
            ppv = evaluate_ppv(preds, native_map[prot], top_fraction=2.0, seq_length=L)
            ppv_lr = compute_ppv_long(preds, native_map[prot], top_fraction=2.0, seq_length=L)
            
            bench_summary.append((prot, ppv, ppv_lr, beff, L))
        else:
            print(f"Warning: missing layer 5 for {prot}")
    # write benchmark_summary.csv
    out2 = os.path.join(project_root, 'benchmark_summary.csv')
    with open(out2,'w',newline='') as f:
        w=csv.writer(f)
        w.writerow(['Protein','PPV','PPV_long','Beff','Length'])
        for prot, ppv,ppv_lr, beff, L in sorted(bench_summary):
            w.writerow([
                prot,
                f"{ppv:.3f}",
                f"{ppv_lr:.3f}",
                f"{beff:.1f}",
                str(int(L)),
            ])

    print(f"Wrote {out2}")
if __name__=='__main__':
    if len(sys.argv)!=2:
        print("Usage: python evaluate_all_cases.py <project_root_or_results_or_benchmarkset_dir>")
        sys.exit(1)
    main(sys.argv[1])
