#!/bin/bash

echo "🔄 Starting batch parsing of plmdca.out and phycmap.out..."

for dir in data/*/; do
  echo "📁 Processing directory: $dir"

  # ---- Parse plmdca.out ----
  plm_in="${dir}plmdca.out"
  plm_out="${dir}plmdca_parsed.out"
  if [[ -f "$plm_in" ]]; then
    echo "  🧠 Parsing plmdca.out"
    awk -F',' '{print $1, $2, 0, 8}' "$plm_in" > "$plm_out"
  else
    echo "  ⚠️  plmdca.out not found"
  fi

  # ---- Parse phycmap.out ----
  phy_in="${dir}phycmap.out"
  phy_out="${dir}phycmap_parsed.out"
  if [[ -f "$phy_in" ]]; then
    echo "  🧠 Parsing phycmap.out"
    grep -E '^[0-9]' "$phy_in" | awk '{print $1, $2, 0, 8}' > "$phy_out"
  else
    echo "  ⚠️  phycmap.out not found"
  fi
done

echo "✅ All parsing done."

