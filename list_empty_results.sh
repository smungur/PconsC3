#!/bin/bash

for dir in results/*; do
  if [ -d "$dir" ] && [ -z "$(ls -A "$dir")" ]; then
    echo "$dir"
  fi
done

