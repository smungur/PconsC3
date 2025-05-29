#!/usr/bin/env python3
# This code was developed with the assistance of ChatGPT-4o (OpenAI)

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from collections import Counter
from selenium.common.exceptions import TimeoutException
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_DIR = os.path.join(PROJECT_ROOT, "csv")

# === CONFIGURATION ===
PDB_COLUMN = "Protein"
BENCHMARK_FILE = os.path.join(CSV_DIR, "benchmark_summary.csv")
RESULTS_FILE = os.path.join(CSV_DIR, "results_summary.csv")
SELENIUM_TIMEOUT = 15  # Timeout for page loads in seconds

# === ARCHITECTURE MAPPING FUNCTION ===
def map_architecture(arch_text):
    """
    Map raw architecture description to simplified categories:
    'αβ', 'α', 'β', 'excluded', or 'unknown'.
    """
    arch_text = arch_text.lower()
    if 'a/b' in arch_text or 'a b' in arch_text or 'alpha+beta' in arch_text or 'alpha/beta' in arch_text:
        return 'αβ'
    elif 'alpha' in arch_text:
        return 'α'
    elif 'b' in arch_text or 'extended' in arch_text:
        return 'β'
    elif 'few' in arch_text:
        return 'excluded'
    else:
        return 'unknown'

# === SELENIUM SETUP ===
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# === STEP 1: Read and process benchmark_summary.csv ===
print(f"\n📄 Processing file: {BENCHMARK_FILE}")
df = pd.read_csv(BENCHMARK_FILE)

if PDB_COLUMN not in df.columns:
    raise ValueError(f"❌ Column '{PDB_COLUMN}' not found in {BENCHMARK_FILE}")

# Lists to store results
primary_structures = []  # most common secondary structure per protein
diff_flags = []          # True if domains have differing architectures

for i, name in enumerate(df[PDB_COLUMN]):
    pdb_id = name[:4].lower()
    print(f"\n🌐 [{i+1}/{len(df)}] {name} → PDB ID {pdb_id}")

    # Construct search URL for ECOD/AF2
    search_url = f"http://prodata.swmed.edu/ecod/af2_pdb/search?kw={pdb_id}"
    try:
        driver.get(search_url)
        time.sleep(2)
        # Find links to the domain "Tree view"
        tree_links = driver.find_elements(By.LINK_TEXT, "Tree view")
        domain_ids = [link.get_attribute("href").split("id=")[-1].split("#")[0] for link in tree_links]
    except Exception as e:
        print(f"⚠️ Failed to load search page for {pdb_id}: {e}")
        domain_ids = []

    architectures = []  # raw mapped architectures for each domain

    # For each domain, retrieve architecture info
    for domain_id in domain_ids:
        try:
            driver.set_page_load_timeout(SELENIUM_TIMEOUT)
            domain_url = f"http://prodata.swmed.edu/ecod/af2_pdb/domain/{domain_id}"
            driver.get(domain_url)
            time.sleep(1)

            # Extract page body and parse for line starting with 'A:'
            body_text = driver.find_element(By.TAG_NAME, "body").text
            for line in body_text.splitlines():
                if line.startswith("A:"):
                    raw_arch = line[3:].strip()
                    architectures.append(map_architecture(raw_arch))
                    break
        except TimeoutException:
            print(f"⚠️ Timeout loading domain {domain_id}")
        except Exception as e:
            print(f"⚠️ Unexpected error with domain {domain_id}: {e}")

    # Remove 'excluded' and 'unknown' entries for majority calculation
    valid_archs = [a for a in architectures if a not in ('excluded', 'unknown')]

    # Determine if multiple architectures exist among valid domains
    unique_archs = sorted(set(valid_archs))
    if len(unique_archs) > 1:
        diff_flag = True
        print(f"🔍 {pdb_id} domains have multiple valid architectures: {unique_archs}")
    elif unique_archs:
        diff_flag = False
        print(f"✔️ {pdb_id} domains have a uniform valid architecture: {unique_archs[0]}")
    else:
        diff_flag = False
        print(f"❌ No valid architecture information found for {pdb_id}")

    # Select the most frequent valid architecture as the majority structure
    if valid_archs:
        majority_struct = Counter(valid_archs).most_common(1)[0][0]
    else:
        majority_struct = 'not found'

    primary_structures.append(majority_struct)
    diff_flags.append(diff_flag)

# === Append new column to benchmark CSV ===
df["secondary_structure"] = primary_structures
df.to_csv(BENCHMARK_FILE, index=False)
print(f"\n💾 Updated benchmark with secondary structure column: {BENCHMARK_FILE}")

# === Merge new column into results_summary.csv ===
print(f"\n🔄 Updating results file: {RESULTS_FILE}")
benchmark_struct = df[[PDB_COLUMN, "secondary_structure"]]
results_df = pd.read_csv(RESULTS_FILE)

if PDB_COLUMN not in results_df.columns:
    raise ValueError(f"❌ Column '{PDB_COLUMN}' not found in {RESULTS_FILE}")

# Perform the merge and write the updated file
merged = results_df.merge(benchmark_struct, on=PDB_COLUMN, how="left")
merged.to_csv(RESULTS_FILE, index=False)
print(f"💾 Results file updated with secondary structure column: {RESULTS_FILE}")

# === CLEANUP ===
driver.quit()
print("\n✅ All tasks completed!")

