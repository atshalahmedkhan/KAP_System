# Project purpose

Phase 1 packages a pinned open-source C compression benchmark (zstd) for later x86-to-Arm64 migration and optimization research. No application optimizations were performed in this phase.

# Selected application

- Name: Zstandard (zstd)
- Upstream: https://github.com/facebook/zstd
- Tag: v1.5.7
- Commit: f8745da6ff1ad1e7bab384bd1f9d742439278e99
- License: dual BSD OR GPLv2 (not permissive-only)

# Why it was selected

Highest weighted score among three evaluated candidates (zstd, LZ4, libjpeg-turbo). Reliable `make check`, low benchmark CV (~2.7% in evaluation), deterministic round-trip verification, Make+Docker friendly, and realistic SIMD/optimization opportunities for later phases.

# Requirements

- Windows
- Docker Desktop
- Linux containers
- Docker Buildx

# Project structure

See directories: `candidates/`, `benchmark/`, `scripts/`, `container/`, `docs/`.

# Source pinning

See `benchmark/source.lock`. Fetch with `scripts/fetch-source.ps1` or rely on the Dockerfile git clone of the pinned tag/commit.

# Build commands

```powershell
docker buildx build --platform linux/amd64 --load -t phase1-benchmark:amd64 .
# or
.\scripts\build-amd64.ps1
```

```powershell
docker buildx build --platform linux/arm64 --load -t phase1-benchmark:arm64 .
# or
.\scripts\build-arm64.ps1
```

# Test commands

```powershell
docker run --rm phase1-benchmark:amd64 test
docker run --rm --platform linux/arm64 phase1-benchmark:arm64 test
```

# Benchmark commands

```powershell
docker run --rm phase1-benchmark:amd64 benchmark
docker run --rm --platform linux/arm64 phase1-benchmark:arm64 benchmark
```

# Output verification

```powershell
docker run --rm phase1-benchmark:amd64 verify
```

Verifier prints `Correctness: PASS` or `Correctness: FAIL`. Compression correctness requires decompressed bytes to match the fixed original input.

# AMD64 verification

Build, test, and benchmark on `linux/amd64` as documented in `docs/phase1-verification.md`.

# ARM64/QEMU verification

Build with `--platform linux/arm64` and run with `--platform linux/arm64`. Functional compatibility only under QEMU.

# QEMU limitation

QEMU Arm64 timings are **not** real Arm hardware performance. Do not compare them to amd64 for performance claims. Benchmark output includes `Performance comparison valid: NO` on aarch64.

# Benchmark methodology

- Input: `datagen -g33554432` (32 MiB), baked into the image at build time
- Workload: 10 iterations of single-thread (`-T1`) zstd level 6 compress + decompress
- Correctness: SHA-256 round-trip must match original input
- Target duration: approximately 8–15 seconds on the host amd64 machine

# Reproducing results

See `docs/reproducibility.md`.

# Known limitations

- Candidate Arm64 full upstream test suites under QEMU were abbreviated during screening
- Dual BSD/GPLv2 licensing must be respected for redistributions
- Docker Desktop background load can affect absolute timings

# Next phase

Phase 2 will analyze architecture dependencies and migration risks for the selected application. Phase 2 work was not performed here.