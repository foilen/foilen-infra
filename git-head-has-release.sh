#!/bin/bash

set -e

# Get the directory path of the current script
RUN_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $RUN_PATH

# Check all
for project in $(cat projects.txt); do
  if [ -d "$project" ]; then
    pushd $project > /dev/null
    if [ "$(git tag --points-at)" == "" ] ; then
      echo $project is not released
    fi
    popd > /dev/null
  fi
done
