# PconsC3

Faster, more accurate and entirely open source method for predicting contacts in proteins

> 🔄 This project is adapted from the original [PconsC3 implementation](https://github.com/mskwark/PconsC3) by Marcin J. Skwark and collaborators.

If you use PconsC3 please cite:

* Carlo Baldassi, Marco Zamparo, Christoph Feinauer, Andrea Procaccini, Riccardo Zecchina, Martin Weigt and Andrea Pagnani, (2014) PLoS ONE 9(3): e92721. doi:10.1371/journal.pone.0092721
* Christoph Feinauer, Marcin J. Skwark, Andrea Pagnani, and Erik Aurell. (2014) PLoS Comp Bio: e1003847. doi:10.1371/journal.pcbi.1003847

## 📑 Table of Contents
- PconsC3
    - 📑 Table of Contents
- 📂 Dataset Structure
    - 📁 Access to Required Model Files
        - 📁 Access PconsC3 model files on Google Drive
        - 📦 Automatic download of tree models
        - 📥 Download Required HDF5 Model Files
- ▶️ Running PconsC3
- [🐳 Running with Docker](#-running-with-docker)
- [🐳 Running the Prediction Inside Docker](#-running-the-prediction-inside-docker)
- [📊 Running Batch Experiments (Benchmark Evaluation)](#-running-batch-experiments-benchmark-evaluation)
  - [🧪 Option 1: Run all proteins sequentially](#-option-1-run-all-proteins-sequentially)
  - [⚡ Option 2: Run in parallel by prefix](#-option-2-run-in-parallel-by-prefix)
  - [🔄 Check for missing predictions](#-check-for-missing-predictions)
  - [⚙️ Important – Set treefraction = 03](#️-important--set-treefraction--03)
  - [✅ Evaluate all results](#-evaluate-all-results)
-  🗂️ Project Structure and File Usage
    - 📁 Key Folders
    -  📄 Prediction Scripts
    - 📄 Model Download and Preparation
    - 📄 Batch Processing
    - 📄 Other Files

# 📂 Dataset Structure

This implementation uses the dataset from the article:

> **Michel M, Skwark MJ, Menéndez Hurtado D, Ekeberg M, Elofsson A.**
> *Predicting accurate contacts in thousands of Pfam domain families using PconsC3.*
> Bioinformatics. 2017;33(18):2859–2866. [doi:10.1093/bioinformatics/btx332](https://doi.org/10.1093/bioinformatics/btx332)

The dataset contains **210 protein domains** from the Pfam database as referenced in the article.

All protein input files are organized under the `data/` directory.
Each subdirectory (e.g., `data/1AHSC/`) corresponds to one protein domain and contains the following files:

```
gdca.out
plmdca_parsed.out
phycmap_parsed.out
netsurf.out
psipred.ss2
alignment.stats
alignment.a3m
```

---
## 📁 Access to Required Model Files

Due to GitHub file size limitations, the `.hdf5` files and tree models used by PconsC3 are hosted externally.

👉 [📁 Access PconsC3 model files on Google Drive](https://drive.google.com/drive/folders/1tarnHJf_epacU8_8ZJTnKnlwXqi0MNm7?usp=share_link)

---

### 📦 Automatic download of tree models

To automatically download the tree model files (`tlayer0.zip` to `tlayer5.zip`), use the following script:

```bash
python3 downloadTrees.py
```

This script uses `gdown` to fetch and unzip the required model files.

> 🔧 Requirement: Before running the script, install `gdown`:
> 
> ```bash
> pip install gdown
> ```


### 📥 Download or generate required HDF5 Model Files

#### ✅ Recommended: Download via script (outside Docker)
You have two options to get the required `.hdf5 files` (`tlayer0.hdf5` to `tlayer5.hdf5`):
To download all `.hdf5` model layers automatically, use:

```bash
python3 downloadHDF5.py
```

After downloading:
- Place the `.hdf5` files in the root of the project
- These replace the need for the original `tforest0` to `tforest5` folders
#### 🛠️ Alternative: Convert tree models to HDF5 (inside Docker)
If you already have the tree model folders (`tforest0` to `tforest5`) inside your Docker container, you can convert them to HDF5 format using:
```bash
python3 convert_to_hdf5.py
```
However, **this step is optional** if you use `downloadHDF5.py`, which is the recommended and simpler approach

# ▶️ Running PconsC3

To run the prediction on a given protein (e.g., `1AHSC`), use the following command:

```bash
python3 predict.py \
  data/1AHSC/gdca.out \
  data/1AHSC/plmdca_parsed.out \
  data/1AHSC/phycmap_parsed.out \
  data/1AHSC/netsurf.out \
  data/1AHSC/psipred.ss2 \
  data/1AHSC/alignment.stats \
  data/1AHSC/alignment.a3m \
  /absolute/path/to/PconsC3 \
  0 \
  results/1AHSC/1AHSC_output
```

> 🔁 Replace `/absolute/path/to/PconsC3` with the full path to your local copy of the repository.
> If you are already in the root of the project, you can use `.` instead.

# 🐳 Running with Docker

If you prefer using Docker, you can build and run the container as follows:

```bash
# Build the image (run this from the root of the project)
docker build -t pconsc3 .

# Run the container interactively, mounting the current directory into /app
docker run -it --rm -v $(pwd):/app pconsc3 bash
```

> 💡 **Note for macOS users**:
> Based on personal experience, running PconsC3 natively on macOS may cause compatibility issues.
> Using Docker is therefore the recommended and most reliable method.

### 🔍 Docker command explained

```bash
docker run -it --rm -v $(pwd):/app pconsc3 bash
```

* `-it` : interactive terminal mode — lets you interact with the container
* `--rm` : automatically removes the container after exit
* `-v $(pwd):/app` : mounts your current folder into `/app` inside the container
* `pconsc3` : the name of the Docker image you built
* `bash` : opens a shell in the container so you can run commands

To leave the container after you're done:

```bash
exit
```

## 🐳 Running the Prediction Inside Docker

Once inside the Docker container (see section above), you can run the prediction script using the following command:

```bash
python3 predict.py \
  data/1AHSC/gdca.out \
  data/1AHSC/plmdca.out \
  data/1AHSC/phycmap.out \
  data/1AHSC/netsurf.out \
  data/1AHSC/psipred.ss2 \
  data/1AHSC/alignment.stats \
  data/1AHSC/alignment.a3m \
  /app \
  0 \
  results/1AHSC/1AHSC_output
```

Here are examples of using predict-parallel and predict-parallel-hdf5 where 4 is the number of threads.
```bash
python3 predict-parallel.py \
  data/1AHSC/gdca.out \
  data/1AHSC/plmdca.out \
  data/1AHSC/phycmap.out \
  data/1AHSC/netsurf.out \
  data/1AHSC/psipred.ss2 \
  data/1AHSC/alignment.stats \
  data/1AHSC/alignment.a3m \
  /app \
  0 \
  results/1AHSC/1AHSC_output
  4
```

```bash
python3 predict-parallel-hdf5.py \
  data/1AHSC/gdca.out \
  data/1AHSC/plmdca.out \
  data/1AHSC/phycmap.out \
  data/1AHSC/netsurf.out \
  data/1AHSC/psipred.ss2 \
  data/1AHSC/alignment.stats \
  data/1AHSC/alignment.a3m \
  /app \
  0 \
  results/1AHSC/1AHSC_output
  4
```
# 📊 Running Batch Experiments (Benchmark Evaluation)

Once inside the Docker container, you can run large-scale predictions on all proteins in the benchmark.

---

## 🧪 Option 1: Run all proteins sequentially

This method uses a single script to run predictions on every protein found in the `data/` folder:

```bash
python3 batch_predict_hdf5.py
```
⏱ **Estimated time**: ~3 to 4 hours (single process)


## ⚡ Option 2: Run in parallel by prefix
To speed up execution, open **four terminals** (or use a multiplexer like `tmux`) and run:
```bash
python3 batch_1.py
python3 batch_2.py
python3 batch_3.py
python3 batch_4.py

```
Each script runs `predict-parallel-hdf5.py` on all proteins whose names start with `1`, `2`, `3`, or `4`.

⏱ **Estimated time**: ~1 to 2 hours total (multi-process, parallel)

## 🔄 Check for missing predictions
After batch execution, you can recover any failed or missing runs with:
```bash
python3 launch_missing_predictions.py
```
This script checks `results/<protein>/` for the file `<protein>_output.l5`, and only runs missing ones

## Important – Set treefraction = 0.3
In `predict-parallel-hdf5.py`, make sure the following line is set:
```python
treefraction = 0.3
```
This setting avoids memory issues on large proteins like 1C9YA, and is also the recommended default from the original PconsC3 repository.

## Files on which the program does not work
 predict-parallel-hdf5.py works on 1XQFA, with treefraction = 0.2.
 It does not work on: 2FEEB, 3PJZA, 3QE7A and 3QNQA
 
# ✅ Evaluation of the results
 
 ## 📊 1. Evaluate prediction performance (PPV, Beff, etc.)
    Run the following script to evaluate predictions from both `results/` and `benchmarkset/`:
    ```bash
    python3 scripts/evaluate_all_cases.py
    ```
    This generates two CSV files inside the `csv/` directory:
        - `results_summary.csv`
        - `benchmark_summary.csv`
    Each file includes:
        - `PPV`: precision for top L×2 contacts,
          - `PPV_long`: precision for long-range contacts (|i−j| ≥ 24),
          - `B_eff` effective number of sequences (at 90% identity threshold).
          
## 👥 2. Add family size (number of aligned sequences)
To compute and append the raw family size for each protein:
 ```bash
    python3 scripts/count_family_size.py
```
This adds the `FamilySize` column to both `results_summary.csv` and `benchmark_summary.csv`.

##🧬 3. Annotate secondary structure from ECOD
To assign secondary structure classes based on ECOD domain annotations:
 ```bash
    python3 scripts/annotate_secondary_structure.py
```
This script adds two new columns:
    - `secondary_structure_majority`: most common structure (α, β, αβ…),
    -  `domains_diff_architecture`: `True` if domains have mixed architectures.
Let me know if you'd like me to directly apply this to your `README.md` file and send you the updated version.
    

# Making PconsC3 run faster

There are a few parameters in `./predict.py` that can be tweaked, notably:

* `maxtime` -- the maximum time in seconds spent on a single prediction layer (total prediction time will be at most 6x maxtime + time spent on i/o). For the larger proteins setting maxtime too low may result in sub-par performance
* `treefraction` -- the fraction of trees to be used. While we recommend leaving `treefraction` set to 1., benchmarks have demonstrated satisfactory performance at values as low as `0.3` and for proteins with a lot of sequence information, as low as `0.1`.

# 🗂️ Project Structure and File Usage

This section provides an overview of the main files and folders in the project, and their roles.

## 📁 Key Folders

- `data/`: Contains the input files for the 210 protein domains used in the benchmark dataset.
- `results/`: Output directory for predictions. For each protein, a subfolder contains the corresponding prediction files.
- `benchmarkset/`: Auxiliary data for benchmarking (usage depends on scripts like `evaluate_all_cases.py`).
- 'csv/': Contains benchmark_summary et results_summary.csv, which contains information about the folder `benchmarkset/` and `results/`.
- 'scripts/': Contains scripts which generate and manipulate the csv files, in the folder 'csv/'
---

## 📄 Prediction Scripts

- `predict.py`: Basic prediction script (single-threaded).
- `predict-parallel.py`: Parallel prediction using the Cython module `_predict_parallel.pyx`.
- `predict-parallel-hdf5.py`: Parallel + HDF5-based version (also uses `_predict_parallel.pyx`) — most efficient for large proteins.
- `_predict_parallel.pyx`: script called by 


> ⚠️ For large proteins like `1C9YA`, you must set `treefraction = 0.3` in the parallel scripts to avoid memory crashes.

---

## 📄 Model Download and Preparation

- `downloadTrees.py`: Downloads `.zip` tree models (`tlayer0.zip` to `tlayer5.zip`) from Google Drive.
- `convert_to_hdf5.py`: Converts unzipped tree model folders into `.hdf5` files (requires running inside Docker).
- `downloadHDF5.py`: 🟢 **Recommended** — downloads ready-to-use `.hdf5` models directly.
- `download_pdbs_for_all.py`: Downloads `.pdb` files for proteins in `data/` — used for evaluation scripts.

---

## 📄 Batch Processing

- `batch_predict_hdf5.py`: Predicts all proteins sequentially (slow, 3–4h).
- `batch_1.py`, `batch_2.py`, `batch_3.py`, `batch_4.py`: Run predictions in parallel by prefix (faster, 1–2h total).
- `launch_missing_predictions.py`: Re-runs predictions for any proteins that failed or are missing output.
- `evaluate_all_cases.py`: Computes metrics (Precision, Recall, etc.) and outputs them into `results_summary.csv`.

---

## Results Evaluation


___
### 📄 Other Files


# Help and Support

If you run into any problems with the software or observe it performing poorer than expected, we would appreciate an email to Marcin J. Skwark ([firstname@lastname.pl](mailto:firstname@lastname.pl) or [firstname.middleinitial.lastname@vanderbilt.edu](mailto:firstname.middleinitial.lastname@vanderbilt.edu)).
