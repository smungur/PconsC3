import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from collections import Counter

# === CONFIG ===
FILES_TO_PROCESS = [
    ("benchmark_summary.csv", "benchmark_with_class.csv"),
    ("results_summary.csv", "results_with_class.csv")
]
PDB_COLUMN = "Protein"

# === MAPPING FUNCTION ===
def map_architecture(arch_text):
    arch_text = arch_text.lower()
    if 'a/b' in arch_text or 'a b' in arch_text or 'alpha+beta' in arch_text or 'alpha/beta' in arch_text:
        return 'αβ'
    elif 'alpha' in arch_text:
        return 'mainly-α'
    elif 'b' in arch_text or 'extended' in arch_text:
        return 'mainly-β'
    elif 'few' in arch_text:
        return 'excluded'
    else:
        return 'unknown'

# === SELENIUM SETUP ===
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# === PROCESS EACH CSV ===
for input_csv, output_csv in FILES_TO_PROCESS:
    print(f"\n📄 Processing: {input_csv}")
    df = pd.read_csv(input_csv)

    if PDB_COLUMN not in df.columns:
        print(f"❌ Column '{PDB_COLUMN}' not found in {input_csv}")
        continue

    structure_classes = []

    for i, name in enumerate(df[PDB_COLUMN]):
        pdb_id = name[:4].lower()
        print(f"\n🌐 [{i+1}/{len(df)}] {name} → PDB ID {pdb_id}")

        search_url = f"http://prodata.swmed.edu/ecod/af2_pdb/search?kw={pdb_id}"
        driver.get(search_url)
        time.sleep(2)

        tree_links = driver.find_elements(By.LINK_TEXT, "Tree view")
        domain_ids = [link.get_attribute("href").split("id=")[-1].split("#")[0] for link in tree_links]

        found_classes = []

        final_class = "not found"

        if domain_ids:
            domain_id = domain_ids[0]  # ⬅️ Only take the first one
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
            except Exception as e:
                print(f"⚠️ Error loading {domain_id}: {e}")
        else:
            final_class = "not found"

        print(f"✅ Final class: {final_class}")
        structure_classes.append(final_class)

    df["secondary_structure_class"] = structure_classes
    df.to_csv(output_csv, index=False)
    print(f"\n💾 Saved: {output_csv}")

# === CLEANUP ===
driver.quit()
print("\n✅ All done!")

