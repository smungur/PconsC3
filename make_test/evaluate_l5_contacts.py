#!/usr/bin/env python3

import argparse

def parse_l5(filepath, top_n=None):
    contacts = []
    with open(filepath) as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            i, j, score = map(float, parts[:3])
            contacts.append((int(i), int(j), score))
    contacts.sort(key=lambda x: x[2], reverse=True)
    return contacts[:top_n] if top_n else contacts

def load_true_contacts(filepath):
    true_contacts = set()
    with open(filepath) as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            i, j = map(int, parts[:2])
            true_contacts.add((min(i, j), max(i, j)))
    return true_contacts

def precision_at_k(predicted, true_contacts, k):
    top_pred = predicted[:k]
    correct = sum(1 for i, j, _ in top_pred if (min(i, j), max(i, j)) in true_contacts)
    return correct / k if k else 0

def main():
    parser = argparse.ArgumentParser(description="Evaluate contact prediction precision from .l5 file")
    parser.add_argument('--pred', required=True, help="Predicted .l5 contact file")
    parser.add_argument('--true', required=True, help="True contact file (e.g., from PDB)")
    parser.add_argument('--length', type=int, required=True, help="Length of the protein sequence (L)")

    args = parser.parse_args()

    pred = parse_l5(args.pred)
    truth = load_true_contacts(args.true)
    L = args.length

    print(f"Evaluating {args.pred} vs {args.true}")
    print(f"Total predicted contacts: {len(pred)}")
    print(f"Total true contacts: {len(truth)}\n")

    for factor in [1, 2, 5, 10]:
        k = max(1, L // factor)
        prec = precision_at_k(pred, truth, k)
        print(f"Precision @L/{factor:<2}: {prec:.3f} (Top {k} predictions)")

if __name__ == "__main__":
    main()

