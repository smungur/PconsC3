import os
#pip install gdown

# Replace these with your actual file IDs from Google Drive
files = {
    "tlayer0.zip": "15JsnIvxwSQPdGfw9sxRwRnRIXytq5_1K",
    "tlayer1.zip": "1PRcyOKirDsRoBDqJY6slEaL9i9cFQxbP",
    "tlayer2.zip": "1I3AWhOZ7QXoD4rOyV9B9kKTE0gWTstDi",
    "tlayer3.zip": "1bDdM2o8rGK5vXDuNuKFkJj1WiFW1doNY",
    "tlayer4.zip": "1OLAx1Ffl1pyQDpAreX4h5Buh71tM3hTO",
    "tlayer5.zip": "1TCcq0EV3T0hRzdI0PXEJ0rvS54IlI2Z-",
}


def download_from_drive(file_name, file_id):
    print(f"⬇️  Downloading {file_name}...")
    os.system(f"gdown --id {file_id} -O {file_name}")
    print(f"📦 Unzipping {file_name}...")
    os.system(f"unzip -o {file_name}")
    print(f"✅ {file_name} ready.\n")


if __name__ == "__main__":
    for name, file_id in files.items():
        download_from_drive(name, file_id)
