#!/bin/bash

set -e

# Get the directory path of the current script
RUN_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $RUN_PATH

# Clone all
for project in $(cat projects.txt); do
  if [ -d "$project" ]; then
    echo Project $project already exists. Skipping
  else
    echo Cloning project $project
    git clone git@github.com:foilen/$project.git $project
  fi
done
