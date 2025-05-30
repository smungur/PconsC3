# PconsC3

Faster, more accurate, and entirely open-source method for predicting residue–residue contacts in proteins.

> 🔄 This version is adapted from the original [PconsC3 implementation](https://github.com/mskwark/PconsC3) by Marcin J. Skwark and collaborators, with extensions for batch evaluation and structure annotation.
> All original files remain under GPL-2.0; our extensions below are also under GPL-2.0.

---

##  ⚖️ License

This project is released under the GPL-2.0 license. See the [LICENSE](../LICENSE) file for details

---

## 📚 Citations

If you use **PconsC3**, please cite:

- Carlo Baldassi, Marco Zamparo, Christoph Feinauer, Andrea Procaccini, Riccardo Zecchina, Martin Weigt, and Andrea Pagnani.  
  *PLoS ONE* **9**(3): e92721 (2014).  
  [https://doi.org/10.1371/journal.pone.0092721](https://doi.org/10.1371/journal.pone.0092721)

- Christoph Feinauer, Marcin J. Skwark, Andrea Pagnani, and Erik Aurell.  
  *PLoS Computational Biology* **10**(10): e1003847 (2014).  
  [https://doi.org/10.1371/journal.pcbi.1003847](https://doi.org/10.1371/journal.pcbi.1003847)

---

## 📑 Table of Contents

- PconsC3
  -  ⚖️ [License](#-license)
  - 📚 [Citations](#-citations)
  - 📑 Table of Contents 
- 📂 Dataset Structure  
  - 📁 [Access to Required Model Files](#-access-to-required-model-files)  
    - 🔗 [Access PconsC3 model files on Google Drive](#-access-pconsc3-model-files-on-google-drive)  
    - 📦 [Automatic download of tree models](#-automatic-download-of-tree-models)  
    - 📥 [Download Required HDF5 Model Files](#-download-required-hdf5-model-files)  
      - ✅ Recommended: Download via script (outside Docker)  
      - 🛠️ Alternative: Convert tree models to HDF5 (inside Docker)  
- ▶️ Running PconsC3  
  - 🐳 [Running with Docker](#-running-with-docker)  
    - 🔍 Docker command explained  
  - 🐳 [Running the Prediction Inside Docker](#-running-the-prediction-inside-docker)  
- 📊 [Running Batch Experiments (Benchmark Evaluation)](#-running-batch-experiments-benchmark-evaluation)  
  - 🧪 [Option 1: Run all proteins sequentially](#-option-1-run-all-proteins-sequentially)  
  - ⚡ [Option 2: Run in parallel by prefix](#-option-2-run-in-parallel-by-prefix)  
  - 🔄 [Check for missing predictions](#-check-for-missing-predictions)  
  - ⚙️ [Important – Set treefraction = 0.3](#️-important--set-treefraction--03)  
  - ✅ [Evaluate all results](#-evaluate-all-results)  
    - 📊 1. Evaluate prediction performance (PPV, Beff, etc.)  
    - 👥 2. Add family size (number of aligned sequences)  
    - 🧬 3. Annotate secondary structure from ECOD  
- 🗂️ [Project Structure and File Usage](#-project-structure-and-file-usage)  
  - 📁 [Key Folders](#-key-folders)  
  - 📄 [Prediction Scripts](#-prediction-scripts)  
  - 📄 [Model Download and Preparation](#-model-download-and-preparation)  
  - 📄 [Batch Processing](#-batch-processing)  


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
structure.pdb ← (required for evaluation scripts)
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

Where:
* `data/1AHSC/` contains all required input files for the protein **1AHSC**
* `/app` is the model directory inside the container
* `0` refers to the **MaxDepth** parameter
    * `0` disables tree depth limitation (recommended).
* `results/1AHSC/1AHSC_output` is the output file prefix

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

Where:
* `4` is the number of thread

# 🔧 Performance Tip: Adjusting `treefraction`

To speed up prediction and reduce memory usage, you can lower the `treefraction` parameter:

- Default: `treefraction = 1.0`
- Recommended: `treefraction = 0.3`
- For large families: even `treefraction = 0.1` can work

Reducing this value decreases the number of decision trees used in prediction (with minimal loss in accuracy).

# 📊 Running Batch Experiments (Benchmark Evaluation)

Once inside the Docker container, you can run large-scale predictions on all proteins in the benchmark.

> ⚠️ **Important:** All scripts inside the `batch/` folder — including `batch_predict_hdf5.py` and `launch_missing_predictions.py` — must be executed **from the project root** (`/app` in Docker):
>
> ✅ Correct:
> ```bash
> python3 batch/batch_4.py
> ```
>
> ❌ Incorrect:
> ```bash
> cd batch
> python3 batch_4.py  # 🚫 Will fail: cannot locate paths like /app/data
> ```

---

## 🧪 Option 1: Run all proteins sequentially

This method uses a single script to run predictions on every protein found in the `data/` folder:

```bash
python3 batch/batch_predict_hdf5.py
```
⏱ **Estimated time**: ~3 to 4 hours (single process)


## ⚡ Option 2: Run in parallel by prefix
To speed up execution, open **four terminals** and run:
```bash
python3 batch/batch_1.py
python3 batch/batch_2.py
python3 batch/batch_3.py
python3 batch/batch_4.py

```
Each script runs `predict-parallel-hdf5.py` on all proteins whose names start with `1`, `2`, `3`, or `4`.

⏱ **Estimated time**: ~1 to 2 hours total (multi-process, parallel)

## 🔄 Check for missing predictions
After batch execution, you can recover any failed or incomplete runs with:
```bash
python3 batch/launch_missing_predictions.py
```
This script checks each folder under `results/` for the presence of the expected output file (`<protein>_output.l5`), and re-runs predictions only for missing cases.

## Important – Set treefraction = 0.3
In `predict-parallel-hdf5.py`, make sure the following line is set:
```python
treefraction = 0.3
```
This setting avoids memory issues on large proteins like 1C9YA, and is also the recommended default from the original PconsC3 repository.

## Files on which the program does not work
 predict-parallel-hdf5.py works on `1XQFA`, with treefraction = `0.2`.
 It does not work on: `2FEEB`, `3PJZA`, `3QE7A` and `3QNQA`
 
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
- B<sub>eff</sub> effective number of sequences (at 90% identity threshold).

⏱ **Estimated time**: ~6 to 7 minutes
          
## 👥 2. Add family size (number of aligned sequences)
To compute and append the raw family size for each protein:
 ```bash
    python3 scripts/count_family_size.py
```
This adds the `FamilySize` column to both `results_summary.csv` and `benchmark_summary.csv`.

## 🧬 3. Annotate secondary structure from ECOD
To assign secondary structure classes based on ECOD domain annotations:
 ```bash
    python3 scripts/annotate_secondary_structure.py
```
This script add one new column:
- `secondary_structure_majority`: most common structure (`α`, `β`, `αβ`, etc.),

⏱ **Estimated time**: ~2 hours total

This script uses `selenium` to automate the retrieval of domain annotations from the ECOD website.

> 🔧 Requirement: Before running the script, install `selenium`:
> 
> ```bash
> pip install selenium
> ```
You will also need to have **ChromeDriver** installed and available in your system `PATH`.

# 🗂️ Project Structure and File Usage

This section provides an overview of the main files and folders in the project, and their roles.

## 📁 Key Folders

- `data/`: Contains input files (e.g. alignments, predictions, structure) for the 210 protein domains used in the benchmark.

- `results/`: Stores output predictions. Each subdirectory corresponds to one protein and contains its `.l5` prediction files.

- `benchmarkset/`: Contains reference prediction data used for evaluation (processed similarly to `results/`).

- `csv/`: Contains summary CSV files generated by evaluation scripts:
  - `results_summary.csv`: Evaluation results for predictions in `results/`
  - `benchmark_summary.csv`: Evaluation results for predictions in `benchmarkset/`

- `scripts/`: Contains all evaluation and preprocessing scripts that generate and manipulate the CSV files in the `csv/` folder.

- `batch/`: Contains batch processing scripts used to run predictions across many proteins

- 
---

## 📄 Prediction Scripts

- `predict.py`: Basic prediction script (single-threaded).
- `predict-parallel.py`: Parallel prediction using the Cython module `_predict_parallel.pyx`.
- `predict-parallel-hdf5.py`: Parallel + HDF5-based version (also uses `_predict_parallel.pyx`) — most efficient for large proteins.
- `_predict_parallel.pyx`: Core Cython module used by both parallel scripts. Implements optimized loops for speed.



> ⚠️ For large proteins like `1C9YA`, you must set `treefraction = 0.3` in the parallel scripts to avoid memory crashes.

---

## 📄 Model Download and Preparation

Scripts to retrieve and prepare PconsC3 model files:

- `downloadTrees.py`: Downloads `.zip` tree models (`tlayer0.zip` to `tlayer5.zip`) from Google Drive.
- `convert_to_hdf5.py`: Converts unzipped tree model folders into `.hdf5` files (requires running inside Docker).
- `downloadHDF5.py`: 🟢 **Recommended** — downloads ready-to-use `.hdf5` models directly.
- `download_pdbs_for_all.py`: Downloads `.pdb` files for proteins in `data/` — used for evaluation scripts.

---

## 📄 Batch Processing

Scripts to run predictions across many proteins:

- `batch_predict_hdf5.py`: Predicts all proteins sequentially (slow, 3–4h).
- `batch_1.py`, `batch_2.py`, `batch_3.py`, `batch_4.py`: Run predictions in parallel by prefix (faster, 1–2h total).
- `launch_missing_predictions.py`: Re-runs predictions for any proteins that failed or are missing output.

---

## 📄 Results Evaluation

Scripts to compute and enrich evaluation metrics:

- `evaluate_all_cases.py`: Computes:
    - `PPV`: precision on top L×2 contacts
    - `PPV_long`: precision on long-range contacts (|i–j| ≥ 24)
    -  B<sub>eff</sub>: effective sequence count 

         Outputs:
        - `csv/benchmark_summary.csv`
        - `csv/results_summary.csv`
      
- `count_family_size.py`: Adds a `FamilySize` column (number of aligned sequences in the `.a3m`file) to each summary file.
- `annotate_secondary_structure`: Annotates proteins with structural class using ECOD domain info.
    Adds column:
        - `annotate_secondary_structure`
  

___

