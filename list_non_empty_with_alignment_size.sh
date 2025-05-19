#!/bin/bash

for dir in results/*; do
  if [ -d "$dir" ] && [ "$(find "$dir" -mindepth 1 -print -quit)" ]; then
    name=$(basename "$dir")
    alignment_file="data/$name/alignment.a3m"
    if [ -f "$alignment_file" ]; then
      count=$(grep -c "^>" "$alignment_file")
      echo "$dir is NOT empty | $alignment_file has $count sequences"
    else
      echo "$dir is NOT empty | $alignment_file not found"
    fi
  fi
done

