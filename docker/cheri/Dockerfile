FROM debian:10

RUN apt-get update
RUN apt-get install -y libtool pkg-config clang bison cmake ninja-build samba flex texinfo libglib2.0-dev libpixman-1-dev libarchive-dev libarchive-tools libbz2-dev libattr1-dev libcap-ng-dev python-dev libmpfr-dev libexpat-dev libpython-dev git

WORKDIR /root

RUN git clone https://github.com/CTSRD-CHERI/cheribuild.git \
        && cd cheribuild \
        && git checkout 10733147e875923974d172f04f2e0bcc08179e17

RUN git clone https://github.com/CTSRD-CHERI/llvm-project.git \
        && cd llvm-project \
        && git checkout fae644257050a3b1ec2cb1ee56d29643a77e26e4

RUN git clone https://github.com/CTSRD-CHERI/qemu.git \
        && cd qemu \
        && git checkout 24c4f92aac23b5d34454feafd25a9596db326dfd \
        && git submodule update --init --recursive

RUN git clone https://github.com/CTSRD-CHERI/cheribsd.git \
        && cd cheribsd \
        && git checkout 70d364d1cc8e77790d786751c2f5531cd29d8575

RUN git clone https://github.com/CTSRD-CHERI/gdb.git \
        && cd gdb \
        && git checkout d6b055eb61eebf176e2c218f0e88a41dbb78f90f

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update llvm

RUN apt-get install -y libpython3-dev

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update gdb-native

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update qemu cheribsd-riscv64-purecap

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update cheribsd-sysroot-riscv64-purecap

RUN git clone https://github.com/CTSRD-CHERI/riscv-pk.git bbl \
        && cd bbl \
        && git checkout 120e6c2777a2528055e65f6d1b7e3e442c6a0109

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update bbl

RUN rm -rf ./output/sdk/sysroot-riscv64-hybrid ./output/sdk/sysroot-riscv64-purecap ./output/sdk/cheribsd-sysroot-riscv64-purecap-sysroot.tar.gz

COPY cheri-sysroot.tar.gz /root/
RUN mkdir ./output/sdk/sysroot && tar -C ./output/sdk/sysroot -xzvf cheri-sysroot.tar.gz

FROM debian:10

COPY --from=0 /root/output/sdk /opt/cheri/sdk
COPY kernel-cheri.elf /opt/cheri/
COPY disk-image-cheri.img.zst /opt/cheri/

RUN apt-get update
RUN apt-get install -y libpython3.7 libmpfr6 libglib2.0 libpixman-1-0 flex make libarchive13 expat zstd

ENV PATH "/opt/cheri/sdk/bin:${PATH}"
ENV CHERI_SYSROOT "/opt/cheri/sdk/sysroot"

WORKDIR /root
