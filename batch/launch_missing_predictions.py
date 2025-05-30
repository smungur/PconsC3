#!/usr/bin/env python3
# This code was developed with the assistance of ChatGPT-4o (OpenAI)

import os
import subprocess

# Iterate over all subdirectories in the data folder
for protein in sorted(os.listdir("data")):
    input_dir = f"data/{protein}"
    output_file = f"results/{protein}/{protein}_output.l5"

    #print(f"✅ Already exists: {output_file}")
    # Skip if it's not a directory
    if not os.path.isdir(input_dir):
        continue
    # Skip if the output already exists
    if os.path.exists(output_file):
        print(f"✅ Already exists: {output_file}")
        continue

    # Log and create result directory if needed
    print(f"🚀 Predicting: {protein}")
    os.makedirs(f"results/{protein}", exist_ok=True)

    # Build the command to run predict-parallel-hdf5.py
    cmd = [
        "python3", "predict-parallel-hdf5.py",
        f"{input_dir}/gdca.out",
        f"{input_dir}/plmdca.out",
        f"{input_dir}/phycmap.out",
        f"{input_dir}/netsurf.out",
        f"{input_dir}/psipred.ss2",
        f"{input_dir}/alignment.stats",
        f"{input_dir}/alignment.a3m",
        "/app",                  # Path to model directory
        "0",                     # Layer index
        f"results/{protein}/{protein}_output",  # Output base name (output.l5)
        "1"                      # Number of threads
    ]

    # Run the prediction
    subprocess.run(cmd)

