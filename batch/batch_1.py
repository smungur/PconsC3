#!/usr/bin/env python3
# This code was developed with the assistance of ChatGPT-4o (OpenAI)

import os
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
MODEL_DIR = "/app"

def main():
    for name in sorted(os.listdir(DATA_DIR)):
        if not name.startswith("1"):  # prefix for batch_1
            continue
        prot_dir = os.path.join(RESULTS_DIR, name)
        os.makedirs(prot_dir, exist_ok=True)
        output_prefix = os.path.join(prot_dir, f"{name}_output")
        args = [
            "python3", "predict-parallel-hdf5.py",
            os.path.join(DATA_DIR, name, "gdca.out"),
            os.path.join(DATA_DIR, name, "plmdca.out"),
            os.path.join(DATA_DIR, name, "phycmap.out"),
            os.path.join(DATA_DIR, name, "netsurf.out"),
            os.path.join(DATA_DIR, name, "psipred.ss2"),
            os.path.join(DATA_DIR, name, "alignment.stats"),
            os.path.join(DATA_DIR, name, "alignment.a3m"),
            MODEL_DIR,
            "0",
            output_prefix,
            "4"
        ]
        print(f"Running prediction for {name}")
        subprocess.run(args)

if __name__ == '__main__':
    main()

