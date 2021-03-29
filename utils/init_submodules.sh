#! /usr/bin/env bash

git submodule update --init --recursive
git submodule sync

cd BESSPIN-LFS
git-lfs pull
cd ..
