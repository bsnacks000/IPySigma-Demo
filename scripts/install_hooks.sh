#!/usr/bin/env bash

GIT_DIR=$(git rev-parse --git-dir)

echo "Installing pre-commit hooks..."  
# this command creates symlink to our pre-push script
ln -s ../../scripts/pre_commit.sh $GIT_DIR/hooks/pre-commit  
echo "Done" 