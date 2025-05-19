import os
import subprocess

for protein in sorted(os.listdir("data")):
    if not protein.startswith("2"):
        continue
    out_dir = f"results/{protein}"
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "python3", "predict-parallel-hdf5.py",
        f"data/{protein}/gdca.out",
        f"data/{protein}/plmdca.out",
        f"data/{protein}/phycmap.out",
        f"data/{protein}/netsurf.out",
        f"data/{protein}/psipred.ss2",
        f"data/{protein}/alignment.stats",
        f"data/{protein}/alignment.a3m",
        "/app", "0", f"{out_dir}/{protein}_output", "1"
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd)

