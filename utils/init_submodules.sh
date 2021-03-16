#! /usr/bin/env bash

git submodule update --init --recursive
git submodule sync

cd SSITH-FETT-Binaries
git-lfs pull
cd ..
