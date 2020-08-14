# Dockerfiles for building toolchain images

 The `cheri/` and `michigan/` directories contain Dockerfiles for
 building the toolchains from SRI-Cambridge and Michigan. Each
 Dockerfile requires some files from outside this repo to be in the
 build context. Before building the Michigan image, copy
 `s3://ta1-toolchain-images/morpheus-toolchain-06-21-20.tar.gz` to the
 `michigan/` directory. Before building the SRI-Cambridge image, `cd` to the `cheri/` directory and run the script `copy-files.sh`.

 The most recent versions of the images are stored as tarballs in the
 bucket `s3://ta1-toolchain-images`. For more information about
 actually using the toolchains, consult
 [`TOOLCHAINS.md`](./TOOLCHAINS.md).
