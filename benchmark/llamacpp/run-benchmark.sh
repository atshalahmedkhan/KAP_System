#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly IMAGE_NAME="${LLAMACPP_BENCHMARK_IMAGE:-kap-system/llamacpp-benchmark:e031d956797f}"
readonly PLATFORM="${BENCHMARK_PLATFORM:-linux/$(docker version --format '{{.Server.Arch}}')}"

if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
    docker buildx build \
        --platform "${PLATFORM}" \
        --load \
        --tag "${IMAGE_NAME}" \
        "${SCRIPT_DIR}"
fi

docker run --rm \
    --platform "${PLATFORM}" \
    --env "BENCH_CPU_SET=${BENCH_CPU_SET:-}" \
    --env "BENCH_NICE_LEVEL=${BENCH_NICE_LEVEL:-10}" \
    "${IMAGE_NAME}"
