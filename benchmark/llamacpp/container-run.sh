#!/usr/bin/env bash
set -euo pipefail

readonly BENCHMARK_DIR=/opt/benchmark
readonly WARMUP_ITERATIONS=2
readonly MEASURED_ITERATIONS=7
readonly THREADS="$(nproc)"
readonly TOKEN_OUTPUT_DIR="$(mktemp -d)"
trap 'rm -rf "${TOKEN_OUTPUT_DIR}"' EXIT

first_available_cpu() {
    taskset --cpu-list --pid "$$" | awk -F: '
        {
            gsub(/[[:space:]]/, "", $2)
            split($2, ranges, ",")
            split(ranges[1], first_range, "-")
            print first_range[1]
        }'
}

readonly BENCH_CPU="${BENCH_CPU_SET:-$(first_available_cpu)}"
if [[ -z "${BENCH_CPU}" ]]; then
    echo "cannot determine an available CPU for taskset" >&2
    exit 1
fi

run_once() {
    local output_path="$1"
    taskset --cpu-list --cpu-list "${BENCH_CPU}" \
        nice -n "${BENCH_NICE_LEVEL:-10}" \
        /usr/local/bin/token-id-runner \
            --model "${MODEL_PATH}" \
            --prompt "${PROMPT_PATH}" \
            --seed "${SEED}" \
            --temp "${TEMPERATURE}" \
            --n-predict "${N_PREDICT}" \
            --threads "${THREADS}" > "${output_path}"
}

verify_tokens() {
    "${BENCHMARK_DIR}/verify-output.sh" "$1"
}

for iteration in $(seq 1 "${WARMUP_ITERATIONS}"); do
    token_path="${TOKEN_OUTPUT_DIR}/warmup-${iteration}.tokens"
    run_once "${token_path}"
    verify_tokens "${token_path}"
done

declare -a elapsed_ns=()
for iteration in $(seq 1 "${MEASURED_ITERATIONS}"); do
    token_path="${TOKEN_OUTPUT_DIR}/measured-${iteration}.tokens"
    start_ns="$(date +%s%N)"
    run_once "${token_path}"
    end_ns="$(date +%s%N)"
    verify_tokens "${token_path}"
    elapsed_ns+=("$((end_ns - start_ns))")
done

printf '%s\n' "${elapsed_ns[@]}" | awk '
    { values[NR] = $1 / 1000000000; sum += values[NR] }
    END {
        mean = sum / NR
        for (i = 1; i <= NR; ++i) {
            squared_difference += (values[i] - mean) ^ 2
        }
        stdev = sqrt(squared_difference / NR)
        cv = (stdev / mean) * 100
        printf "state=unspecified iterations=%d mean_seconds=%.6f stdev_seconds=%.6f cv_percent=%.2f\n", NR, mean, stdev, cv
    }'
