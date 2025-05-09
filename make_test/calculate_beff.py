from Bio import SeqIO

def sequence_identity(seq1, seq2):
    seq1 = ''.join([c for c in seq1 if c.isupper()])
    seq2 = ''.join([c for c in seq2 if c.isupper()])
    length = min(len(seq1), len(seq2))
    if length == 0:
        return 0
    matches = sum(a == b for a, b in zip(seq1, seq2))
    return matches / length

def calculate_beff(sequences, threshold=0.9):
    beff = 0
    for i, seq_i in enumerate(sequences):
        count = sum(sequence_identity(seq_i, seq_j) >= threshold for seq_j in sequences)
        beff += 1 / count if count > 0 else 0
    return beff

# --- Main ---
fasta_file = "../data/1AHSC/alignment.a3m"
sequences = [str(record.seq) for record in SeqIO.parse(fasta_file, "fasta")]
beff = calculate_beff(sequences)

print(f"✅ Number of effective sequences (Beff) = {beff:.1f}")

