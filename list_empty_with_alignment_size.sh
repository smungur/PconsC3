#!/bin/bash

for dir in results/*; do
  if [ -d "$dir" ] && [ -z "$(ls -A "$dir")" ]; then
    name=$(basename "$dir")
    alignment_file="data/$name/alignment.a3m"
    if [ -f "$alignment_file" ]; then
      count=$(grep -c "^>" "$alignment_file")
      echo "$dir is empty | $alignment_file has $count sequences"
    else
      echo "$dir is empty | $alignment_file not found"
    fi
  fi
done

