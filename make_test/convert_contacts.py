#!/usr/bin/env python3

def convert_contact_matrix_to_pairs(matrix_file, output_file, min_sep=5):
    with open(matrix_file) as f:
        lines = f.readlines()

    with open(output_file, "w") as out:
        for i, line in enumerate(lines):
            values = line.strip().split()
            for j, val in enumerate(values):
                if val == '1' and abs(i - j) >= min_sep:
                    out.write(f"{i+1} {j+1}\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python convert_contacts.py input_matrix.txt output_pairs.txt")
        sys.exit(1)
    
    convert_contact_matrix_to_pairs(sys.argv[1], sys.argv[2])
    print(f"Converted {sys.argv[1]} to contact pairs in {sys.argv[2]}")

