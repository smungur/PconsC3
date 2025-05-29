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


# === CONFIG ===
PDB_COLUMN = "Protein"
benchmark_file = os.path.join(CSV_DIR, "benchmark_summary.csv")
results_file   = os.path.join(CSV_DIR, "results_summary.csv")
# === MAPPING FUNCTION ===
def map_architecture(arch_text):
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

# === STEP 1: Process benchmark_summary.csv ===
print(f"\n📄 Processing: {benchmark_file}")
df = pd.read_csv(benchmark_file)

if PDB_COLUMN not in df.columns:
    raise ValueError(f"❌ Column '{PDB_COLUMN}' not found in {benchmark_file}")

structure_classes = []

for i, name in enumerate(df[PDB_COLUMN]):
    pdb_id = name[:4].lower()
    print(f"\n🌐 [{i+1}/{len(df)}] {name} → PDB ID {pdb_id}")

    search_url = f"http://prodata.swmed.edu/ecod/af2_pdb/search?kw={pdb_id}"
    try:
        driver.get(search_url)
        time.sleep(2)
        tree_links = driver.find_elements(By.LINK_TEXT, "Tree view")
        domain_ids = [link.get_attribute("href").split("id=")[-1].split("#")[0] for link in tree_links]
    except Exception as e:
        print(f"⚠️ Failed to load search page for {pdb_id}: {e}")
        domain_ids = []

    final_class = "not found"

    if domain_ids:
        domain_id = domain_ids[0]
        try:
            driver.set_page_load_timeout(15)
            domain_url = f"http://prodata.swmed.edu/ecod/af2_pdb/domain/{domain_id}"
            driver.get(domain_url)
            time.sleep(1)

            body_text = driver.find_element(By.TAG_NAME, "body").text
            for line in body_text.splitlines():
                if line.startswith("A:"):
                    architecture = line[3:].strip()
                    final_class = map_architecture(architecture)
                    break
        except TimeoutException:
            print(f"⚠️ Timeout loading {domain_id}")
        except Exception as e:
            print(f"⚠️ Unexpected error with {domain_id}: {e}")

    print(f"✅ Final class: {final_class}")
    structure_classes.append(final_class)

df["secondary_structure_class"] = structure_classes
df.to_csv(benchmark_file, index=False)
print(f"\n💾 Updated: {benchmark_file}")

# === STEP 2: Merge into results_summary.csv ===
print(f"\n🔄 Updating: {results_file} using updated benchmark...")

benchmark_struct = df[[PDB_COLUMN, "secondary_structure_class"]]
results_df = pd.read_csv(results_file)

if PDB_COLUMN not in results_df.columns:
    raise ValueError(f"❌ Column '{PDB_COLUMN}' not found in {results_file}")

merged = results_df.merge(benchmark_struct, on=PDB_COLUMN, how="left")
merged.to_csv(results_file, index=False)
print(f"💾 Updated: {results_file} with secondary structure class.")

# === CLEANUP ===
driver.quit()
print("\n✅ All done!")
