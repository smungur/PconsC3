import os
import subprocess
import warnings

def count_sequences(a3m_path):
    if not os.path.exists(a3m_path):
        return 0
    try:
        with open(a3m_path) as f:
            return sum(1 for line in f if line.startswith('>'))
    except Exception as e:
        print(f"[ERROR] Cannot count sequences in {a3m_path}: {e}")
        return 0

# Liste des noms d'identifiants à traiter
names = [name for name in os.listdir("data") if os.path.isdir(os.path.join("data", name))]

for name in sorted(names):
    print(f"[INFO] Processing {name}")

    # Préparation des chemins
    base_dir = os.path.join("data", name)
    files = {
        "gdca": os.path.join(base_dir, "gdca.out"),
        "plm": os.path.join(base_dir, "plmdca_parsed.out"),
        "cmap": os.path.join(base_dir, "phycmap_parsed.out"),
        "netsurf": os.path.join(base_dir, "netsurf.out"),
        "ss2": os.path.join(base_dir, "psipred.ss2"),
        "stats": os.path.join(base_dir, "alignment.stats"),
        "a3m": os.path.join(base_dir, "alignment.a3m")
    }

    # Vérification des fichiers requis
    missing = False
    for key, path in files.items():
        if not os.path.exists(path):
            print(f"[MISSING] {name}: {key} file missing at {path}")
            missing = True
    if missing:
        continue

    # Vérification du nombre de séquences
    seq_count = count_sequences(files["a3m"])
    if seq_count < 10:
        print(f"[SKIP] {name}: only {seq_count} sequences in alignment")
        continue

    # Préparation du dossier de sortie
    out_dir = os.path.join("results", name)
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f"{name}_output")

    # Construction de la commande
    cmd = [
        "python3", "predict-parallel-hdf5.py",
        files["gdca"],
        files["plm"],
        files["cmap"],
        files["netsurf"],
        files["ss2"],
        files["stats"],
        files["a3m"],
        "/app",  # ou autre répertoire de travail
        "0",     # ID ? à ajuster si vous avez du parallélisme
        output_path,
        "4"      # paramètre final du script (index ou worker ?)
    ]

    # Exécution
    ret = subprocess.call(cmd)
    if ret != 0:
        print(f"[ERROR] {name}: prediction script failed with code {ret}")
    else:
        print(f"[OK] {name}: prediction completed")
