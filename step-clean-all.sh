#!/bin/bash

set -e

# Get the directory path of the current script
RUN_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $RUN_PATH

# Clean all
for project in $(cat projects.txt); do
  if [ -d "$project" ]; then
    echo "---[$project]---"
    cd $project
    ./step-clean.sh
    if [ -d "bin" ]; then
      rm -vrf bin
    fi
    find -type f | grep '\.class$' | xargs --no-run-if-empty rm -v
    cd ..
    echo
  fi
done
