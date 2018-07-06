#!/bin/bash

set -e

# Get the directory path of the current script
RUN_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $RUN_PATH

# Clone all
for project in $(cat projects.txt); do
  if [ -d "$project" ]; then
    cd $project

# nothing to commit, working tree clean

    if ! git status | grep 'Your branch is up to date with' > /dev/null || ! git status | grep 'nothing to commit, working tree clean' > /dev/null ; then
      echo "---[$project]---"
      git status
      echo
      git log origin/master..
      echo
    fi
    cd ..
  fi
done
