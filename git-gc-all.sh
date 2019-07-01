#!/bin/bash

set -e

# Get the directory path of the current script
RUN_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $RUN_PATH

# All
for project in $(cat projects.txt); do
  if [ -d "$project" ]; then
    echo "---[$project]---"
    cd $project
    git gc
    cd ..
    echo
  fi
done
