# Two stages, so we can copy over the tarball and unpack it without
# making the final image too large.

FROM alpine:latest

COPY *.tar.gz /tmp/morpheus.tar.gz
RUN mkdir /tmp/morpheus && tar -C /tmp/morpheus -xzf /tmp/morpheus.tar.gz
RUN rm -rf /tmp/morpheus/FreeRTOS-10.0.1/.git

FROM debian:10

RUN apt-get update
RUN apt-get install -y libtinfo5 libxml2 make
RUN mkdir -p /opt/morpheus

COPY --from=0 /tmp/morpheus /opt/morpheus/

ENV PATH "/opt/morpheus/llvm-build/bin:${PATH}"
ENV SYSROOT_DIR "/opt/morpheus/llvm-build/clang_sysroot/riscv32-unknown-elf"
ENV EMTD_PREFIX "/opt/morpheus/llvm-build"
COPY README /opt/morpheus/README

WORKDIR /root
