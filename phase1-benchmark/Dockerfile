# syntax=docker/dockerfile:1
FROM debian:bookworm-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    file \
    git \
    && rm -rf /var/lib/apt/lists/*

ARG ZSTD_TAG=v1.5.7
ARG ZSTD_SHA=f8745da6ff1ad1e7bab384bd1f9d742439278e99

WORKDIR /src
RUN git clone --branch "${ZSTD_TAG}" --depth 1 https://github.com/facebook/zstd.git . \
    && test "$(git rev-parse HEAD)" = "${ZSTD_SHA}" \
    && make -j"$(nproc)" \
    && make -C tests datagen

RUN mkdir -p /opt/benchmark/inputs /opt/benchmark/expected \
    && /src/tests/datagen -g33554432 > /opt/benchmark/inputs/input.bin \
    && sha256sum /opt/benchmark/inputs/input.bin | tee /opt/benchmark/expected/original-input.sha256 \
    && /src/zstd -f -T1 -6 /opt/benchmark/inputs/input.bin -o /opt/benchmark/expected/expected-output.zst \
    && sha256sum /opt/benchmark/expected/expected-output.zst | tee /opt/benchmark/expected/expected-output.sha256 \
    && /src/zstd -f -d /opt/benchmark/expected/expected-output.zst -o /tmp/roundtrip.bin \
    && cmp /opt/benchmark/inputs/input.bin /tmp/roundtrip.bin \
    && rm -f /tmp/roundtrip.bin \
    && cp /src/LICENSE /opt/benchmark/LICENSE \
    && cp /src/COPYING /opt/benchmark/COPYING \
    && printf '%s\n' "${ZSTD_SHA}" > /opt/benchmark/COMMIT \
    && printf '%s\n' "${ZSTD_TAG}" > /opt/benchmark/TAG

FROM debian:bookworm-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    file \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 --shell /bin/bash bench

COPY --from=build /src /opt/zstd-src
COPY --from=build /opt/benchmark /opt/benchmark
COPY container/ /opt/container/

RUN chmod +x /opt/container/*.sh \
    && chown -R bench:bench /opt/benchmark /opt/zstd-src /opt/container \
    && ln -sf /opt/zstd-src/zstd /usr/local/bin/zstd \
    && ln -sf /opt/zstd-src/tests/datagen /usr/local/bin/datagen

ENV BENCH_APP=zstd \
    BENCH_COMMIT=f8745da6ff1ad1e7bab384bd1f9d742439278e99 \
    BENCH_TAG=v1.5.7 \
    BENCH_LEVEL=6 \
    BENCH_ITERS=10 \
    BENCH_THREADS=1 \
    INPUT_PATH=/opt/benchmark/inputs/input.bin \
    EXPECTED_ZST=/opt/benchmark/expected/expected-output.zst \
    WORK_DIR=/tmp/bench-work

USER bench
WORKDIR /home/bench
ENTRYPOINT ["/opt/container/entrypoint.sh"]
CMD ["benchmark"]