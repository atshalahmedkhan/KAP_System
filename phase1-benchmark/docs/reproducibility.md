# Reproducibility

## Host environment

- OS: Windows 10 (build 26200)
- Working directory: KAP_SYSTEM/phase1-benchmark
- Container type: Docker Desktop Linux containers (context desktop-linux)
- Host arch probe: x86_64

## Docker version

- Docker Desktop 4.81.0
- Engine 29.6.1
- Buildx v0.35.0-desktop.2
- Platforms verified: linux/amd64 (uname x86_64), linux/arm64 (uname aarch64 via QEMU)

## Selected source revision

- Upstream: https://github.com/facebook/zstd
- Tag: v1.5.7
- Commit: f8745da6ff1ad1e7bab384bd1f9d742439278e99

## Input generation

Built into the image:

```
datagen -g33554432 > /opt/benchmark/inputs/input.bin
```

Host copy: `benchmark/inputs/input.bin`

## Input checksum

See `benchmark/expected/original-input.sha256` (expected: 35cafdf130f1db75dbfec226ca9a1e100d38c3e26d8c8651808715de10450235).

## Expected output checksum

See `benchmark/expected/expected-output.sha256` and `benchmark/expected/expected-output.zst`.
Mandatory correctness gate is round-trip equality to the original input, not solely compressed bytes.

## Timing methodology

- Wall clock via `date +%s.%N` around the iteration loop inside the container
- Single-thread `-T1`, compression level 6, 10 iterations (packaged)
- Evaluation used 20 iterations (mean ~20.5 s, CV ~2.7%)

## Warm-up policy

No discarded warm-up in packaged runs. Document cold first-run effects if CV rises.

## Number of repetitions

- Tests: 3 (amd64 final)
- Benchmarks: 5 (amd64 final)
- Arm64: functional build/test/benchmark as recorded in phase1-verification.md

## Architecture verification

amd64 native Docker; arm64 via Buildx + QEMU emulation.

## QEMU limitations

Emulated Arm timings are unsuitable for performance comparison with real Arm hardware or with amd64.