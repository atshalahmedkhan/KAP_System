# syntax=docker/dockerfile:1.7

FROM debian:bookworm-slim AS build

ARG LLAMA_CPP_COMMIT=e031d956797f9a10f704fa523fe5fd9b72e9015c
ARG MODEL_REVISION=9217f5db79a29953eb74d5343926648285ec7e67
ARG MODEL_SHA256=7671c0c304e6ce5a7fc577bcb12aba01e2c155cc2efd29b2213c95b18edaf6ed
ARG MODEL_FILE=qwen2.5-0.5b-instruct-q4_0.gguf

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    cmake \
    curl \
    g++ \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git init llama.cpp \
    && cd llama.cpp \
    && git remote add origin https://github.com/ggerganov/llama.cpp.git \
    && git fetch --depth 1 origin "${LLAMA_CPP_COMMIT}" \
    && git checkout --detach FETCH_HEAD \
    && test "$(git rev-parse HEAD)" = "${LLAMA_CPP_COMMIT}"

COPY runner/ /src/runner/
RUN cmake -S /src/runner -B /src/runner/build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /src/runner/build --target token-id-runner --parallel "$(nproc)"

RUN mkdir -p /opt/benchmark/model \
    && curl --fail --location --retry 3 --output "/opt/benchmark/model/${MODEL_FILE}" \
      "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/${MODEL_REVISION}/${MODEL_FILE}" \
    && echo "${MODEL_SHA256}  /opt/benchmark/model/${MODEL_FILE}" | sha256sum --check -

FROM debian:bookworm-slim AS runtime

ARG LLAMA_CPP_COMMIT=e031d956797f9a10f704fa523fe5fd9b72e9015c
ARG MODEL_REVISION=9217f5db79a29953eb74d5343926648285ec7e67
ARG MODEL_SHA256=7671c0c304e6ce5a7fc577bcb12aba01e2c155cc2efd29b2213c95b18edaf6ed
ARG MODEL_FILE=qwen2.5-0.5b-instruct-q4_0.gguf

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    libgomp1 \
    util-linux \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 --shell /bin/bash bench

COPY --from=build /src/runner/build/token-id-runner /usr/local/bin/token-id-runner
COPY --from=build /src/runner/build/bin/ /usr/local/lib/
COPY --from=build /opt/benchmark/model/ /opt/benchmark/model/
COPY prompt.txt /opt/benchmark/prompt.txt
COPY expected/ /opt/benchmark/expected/
COPY container-run.sh verify-output.sh /opt/benchmark/

RUN ldconfig \
    && chmod +x /opt/benchmark/container-run.sh /opt/benchmark/verify-output.sh \
    && chown -R bench:bench /opt/benchmark

ENV LLAMA_CPP_COMMIT=${LLAMA_CPP_COMMIT} \
    MODEL_REVISION=${MODEL_REVISION} \
    MODEL_SHA256=${MODEL_SHA256} \
    MODEL_FILE=${MODEL_FILE} \
    MODEL_PATH=/opt/benchmark/model/${MODEL_FILE} \
    PROMPT_PATH=/opt/benchmark/prompt.txt \
    N_PREDICT=512 \
    SEED=42 \
    TEMPERATURE=0

USER bench
WORKDIR /home/bench
ENTRYPOINT ["/opt/benchmark/container-run.sh"]
