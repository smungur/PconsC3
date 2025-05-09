from pathlib import Path

# === Configuration ===
# Folder where all .l5 files are located
base_dir = Path("result/")

# === Main Script ===
for l5_file in base_dir.rglob("*.l5"):
    # Deduce the base name (e.g., 1AHSC_output)
    base_name = l5_file.stem  # Delete .l5

    # Create the output path
    rr_file = l5_file.with_suffix(".RR")

    # Do not recreate if it already exists (security)
    if rr_file.exists():
        print(f"⚠️ {rr_file.name} already exists. Skipping.")
        continue

    # Read the contents of the .l5 file
    lines = l5_file.read_text().splitlines()

    # Prepare the CASP RR header
    target_name = base_name.split("_output")[0]  # ex: 1AHSC
    header = [
        "PFRMAT RR",
        f"TARGET {target_name}",
        "AUTHOR 0000-0000-0000",
        "PconsC3 METHOD",
        "MODEL 1"
    ]

    # Merge header + content + END
    full_content = header + lines + ["END"]

    # Write the .RR file
    rr_file.write_text("\n".join(full_content))
    print(f"✅ Generated {rr_file.name}")

print("🎯 All done!")
