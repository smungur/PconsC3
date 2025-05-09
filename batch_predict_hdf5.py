import os
import subprocess
import multiprocessing

PREDICT_SCRIPT = "predict-parallel-hdf5.py"
DATA_DIR = "data"
RESULTS_DIR = "results"
FOREST_DIR = "/app"  # ou autre selon ton chemin d'accès dans Docker

#NUM_THREADS = "4"
# Utiliser tous les cœurs moins 2 (mais minimum 1)
max_threads = max(1, multiprocessing.cpu_count() - 2)
NUM_THREADS = str(max_threads)

for protein in sorted(os.listdir(DATA_DIR)):
    folder = os.path.join(DATA_DIR, protein)
    if not os.path.isdir(folder):
        continue

    # Construire les chemins complets vers les fichiers requis
    try:
        files = {
            "gdca": os.path.join(folder, "gdca.out"),
            "plm": os.path.join(folder, "plmdca_parsed.out"),
            "rr": os.path.join(folder, "phycmap_parsed.out"),
            "rsa": os.path.join(folder, "netsurf.out"),
            "ss2": os.path.join(folder, "psipred.ss2"),
            "stats": os.path.join(folder, "alignment.stats"),
            "alignment": os.path.join(folder, "alignment.a3m"),
        }

        # Vérifie que tous les fichiers nécessaires sont présents
        if not all(os.path.isfile(f) for f in files.values()):
            print(f"[SKIP] Missing files for {protein}")
            continue

        output_dir = os.path.join(RESULTS_DIR, protein)
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{protein}_output.hdf5")

        cmd = [
            "python3", PREDICT_SCRIPT,
            files["gdca"],
            files["plm"],
            files["rr"],
            files["rsa"],
            files["ss2"],
            files["stats"],
            files["alignment"],
            FOREST_DIR,
            "0",
            output_file,
            NUM_THREADS
        ]

        print(f"[RUNNING] {protein}")
        subprocess.run(cmd, check=True)

    except Exception as e:
        print(f"[ERROR] {protein}: {e}")

