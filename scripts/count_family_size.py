#!/usr/bin/env python3
# This code was developed with the assistance of ChatGPT-4o (OpenAI)

import os
import glob
import csv
from Bio import SeqIO

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR     = os.path.join(PROJECT_ROOT, "data")
CSV_DIR      = os.path.join(PROJECT_ROOT, "csv")


def count_family_size(aln_path):
    """Count sequences in the given FASTA/A3M file."""
    return sum(1 for _ in SeqIO.parse(aln_path, "fasta"))

def enrich_csv(in_csv, out_csv):
    """
    Read in_csv (must have a 'Protein' column), lookup FamilySize in data/,
    append FamilySize column, and write to out_csv.
    """
    rows = []
    with open(in_csv) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ["FamilySize"]
        for rec in reader:
            prot = rec["Protein"]
            # find alignment file in data/<prot>/*.a3m
            aln_glob = glob.glob(os.path.join(DATA_DIR, prot, "*.a3m"))
            if aln_glob:
                size = count_family_size(aln_glob[0])
            else:
                size = 0  # fallback if missing
            rec["FamilySize"] = size
            rows.append(rec)

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out_csv}")

if __name__ == "__main__":
    # adjust these filenames if yours differ
    enrich_csv(
        os.path.join(CSV_DIR, "results_summary.csv"),
        os.path.join(CSV_DIR, "results_summary_with_size.csv")
    )
    enrich_csv(
        os.path.join(CSV_DIR, "benchmark_summary.csv"),
        os.path.join(CSV_DIR, "benchmark_summary_with_size.csv")
    )
