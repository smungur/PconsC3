#!/usr/bin/env python3
# This code was developed with the assistance of ChatGPT-4o (OpenAI)

import os

# Map of .hdf5 files to their Google Drive file IDs
files = {
    "tlayer0.hdf5": "1ZxOkqWRPfsvm_dHG7Nbzg8uPiJ9Wpd9U",
    "tlayer1.hdf5": "1VFgrqfg9DKcyXorvnV2zdC0vWVDgaWJ-",
    "tlayer2.hdf5": "1BvXW1oO6SzrtfAuSztKzAc2M4_TpRw1w",
    "tlayer3.hdf5": "13JQRu2RhRjMCJlkNCVhSuxRHW7oLFXLd",
    "tlayer4.hdf5": "1UOd3w9q1QIha4eNxErn-WcvJwHItXfUA",
    "tlayer5.hdf5": "1hB1JP7Xe32Y2DMC6Op8ytjkw1i6ddcX7",
}

def download_from_drive(file_name, file_id):
    print(f"⬇️  Downloading {file_name}...")
    os.system(f"gdown {file_id} -O {file_name}")
    print(f"✅ {file_name} ready.\n")

for file_name, file_id in files.items():
    download_from_drive(file_name, file_id)
