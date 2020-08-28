FROM debian:10

RUN apt-get update
RUN apt-get install -y libtool pkg-config clang bison cmake ninja-build samba flex texinfo libglib2.0-dev libpixman-1-dev libarchive-dev libarchive-tools libbz2-dev libattr1-dev libcap-ng-dev python-dev libmpfr-dev libexpat-dev libpython-dev git

WORKDIR /root

RUN git clone https://github.com/CTSRD-CHERI/cheribuild.git \
        && cd cheribuild \
        && git checkout 47d91aedd2ab2bb11da25d05426f33ec3073029f

RUN git clone https://github.com/CTSRD-CHERI/llvm-project.git \
        && cd llvm-project \
        && git checkout d8b11eced5be4ea102cc731a18d6f8e46b523f95

RUN git clone https://github.com/CTSRD-CHERI/qemu.git \
        && cd qemu \
        && git checkout cd4044e3e294256e5b0b8e64e9b67dce55bae69c \
        && git submodule update --init --recursive

RUN git clone https://github.com/CTSRD-CHERI/gdb.git \
        && cd gdb \
        && git checkout 958549a5d72a3e3b56bed892b0996055e8c18b79

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update llvm

RUN apt-get install -y libpython3-dev

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update gdb-native

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update qemu

RUN git clone https://github.com/CTSRD-CHERI/riscv-pk.git bbl \
        && cd bbl \
        && git checkout 120e6c2777a2528055e65f6d1b7e3e442c6a0109

RUN ./cheribuild/cheribuild.py --source-root=/root \
        --skip-update bbl

RUN rm -rf ./output/sdk/sysroot-riscv64-hybrid ./output/sdk/sysroot-riscv64-purecap ./output/sdk/cheribsd-sysroot-riscv64-purecap-sysroot.tar.gz

FROM debian:10

COPY kernel-cheri.elf /opt/cheri/
COPY kernel-cheri-purecap.elf /opt/cheri/
COPY kernel-cheri-temporal.elf /opt/cheri/
COPY disk-image-cheri.img.zst /opt/cheri/
COPY disk-image-cheri-purecap.img.zst /opt/cheri/
COPY disk-image-cheri-temporal.img.zst /opt/cheri/

COPY sysroot /opt/cheri/sdk/sysroot
COPY sysroot-purecap /opt/cheri/sdk/sysroot-purecap
COPY sysroot-temporal /opt/cheri/sdk/sysroot-temporal
COPY researchersREADME.md /root/README.md

RUN apt-get update
RUN apt-get install -y libpython3.7 libmpfr6 libglib2.0 libpixman-1-0 flex make libarchive13 expat zstd

ENV PATH "/opt/cheri/sdk/bin:${PATH}"
ENV CHERI_SYSROOT "/opt/cheri/sdk/sysroot"

WORKDIR /root
