# PconsC3

Faster, more accurate and entirely open source method for predicting contacts in proteins

> 🔄 This project is adapted from the original [PconsC3 implementation](https://github.com/mskwark/PconsC3) by Marcin J. Skwark and collaborators.

If you use PconsC3 please cite:

* Carlo Baldassi, Marco Zamparo, Christoph Feinauer, Andrea Procaccini, Riccardo Zecchina, Martin Weigt and Andrea Pagnani, (2014) PLoS ONE 9(3): e92721. doi:10.1371/journal.pone.0092721
* Christoph Feinauer, Marcin J. Skwark, Andrea Pagnani, and Erik Aurell. (2014) PLoS Comp Bio: e1003847. doi:10.1371/journal.pcbi.1003847

## 📑 Table of Contents
- PconsC3
    - 📑 Table of Contents
- Prerequisites
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


# Prerequisites

* h5py and cython if you want to use the parallel version with hdf5 support (**highly recommended** even for non-parallel usage, see **Parallel version** below.)
* Julia interpreter (ver. 0.3 and up is supported). Present in most Linux repositories (Ubuntu , otherwise download it from [Julia](http://julialang.org/) website.
* Python interpreter (2.7+)
* CD-HIT. Available in most Linux distributions, otherwise downloadable from [GitHub](https://github.com/weizhongli/cdhit)
* A way to generate multiple sequence alignments (or a FASTA formatted MSA).
* A way to generate PSIPRED-like secondary structure predictions
* A way to generate NetSurfP-like solvent accessibility predictions
* An external source of contact information (e.g. PhyCMAP, CMAPpro...), capable of producing contact estimates in CASP RR format

If Julia, Python and CD-HIT are in your search path, you are set to go. Otherwise, you need to either add them to the path, or modify the necessary scripts.

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

Voici des exemples d'utilisation de predict-parallel et predict-parallel-hdf5 où 4 est le nombre de thread.
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
 
 ## ✅ Evaluate all results
 Once all predictions are done, run:
```bash
python3 evaluate_all_cases.py
```
This script computes **Precision**, **Recall**, **F1-score**, and other metrics for each protein, and outputs a summary file:
```bash
results_summary.csv
```
    
# Parallel version and HDF5 support (recommended, even for non-parallel usage)

The parallel version with HDF5 support drastically reduces IO and computation time, while not changing the output in any way. To set it up make sure h5py and Cython are in your PYTHONPATH. You can install the packages via pip:

```
pip install h5py
pip install Cython
```

Then you need to convert the forest data in your PconsC3 root directory into HDF5-files:

```
cd <PconsC3 root directory>
python convert_to_hdf5.py .
```

After successful conversion you can safely remove the folders containing the forest data:

```
find tlayer* ! -name '*.hdf5' -type d -exec rm -r {} +
```

And finally compile the Cython script:

```
python setup.py build_ext -i
```

After that you can run the fast version of PconsC3:

```
./predict-parallel-hdf5.py myprotein.gdca myprotein.0.02.plm20 external.RR netsurf.rsa psipred.ss2 myprotein.stats myprotein.fas outputfile [NumberThreads]
```

# Making PconsC3 run faster

There are a few parameters in `./predict.py` that can be tweaked, notably:

* `maxtime` -- the maximum time in seconds spent on a single prediction layer (total prediction time will be at most 6x maxtime + time spent on i/o). For the larger proteins setting maxtime too low may result in sub-par performance
* `treefraction` -- the fraction of trees to be used. While we recommend leaving `treefraction` set to 1., benchmarks have demonstrated satisfactory performance at values as low as `0.3` and for proteins with a lot of sequence information, as low as `0.1`.

# Help and Support

If you run into any problems with the software or observe it performing poorer than expected, we would appreciate an email to Marcin J. Skwark ([firstname@lastname.pl](mailto:firstname@lastname.pl) or [firstname.middleinitial.lastname@vanderbilt.edu](mailto:firstname.middleinitial.lastname@vanderbilt.edu)).
