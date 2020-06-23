#/bin/bash!

git submodule init
git submodule update
git submodule sync

cd SSITH-FETT-Binaries
git-lfs pull
cd ..