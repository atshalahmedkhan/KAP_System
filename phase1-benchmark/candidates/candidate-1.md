# Zstandard (zstd)

## Repository

- Official URL: https://github.com/facebook/zstd
- Commit SHA: `f8745da6ff1ad1e7bab384bd1f9d742439278e99` (peeled commit for annotated tag `v1.5.7`; tag object `ac66b19e6bd6b83238bf008eecc1298105298532`)
- Release/tag: `v1.5.7`
- License: Dual license — **BSD** OR **GPLv2** (not permissive-only; either license may be used). Upstream files: `LICENSE`, `COPYING`.
- Primary language: C (CLI + `libzstd`)
- Approximate project size: ~few MB source; builds in under a few minutes in Docker

## Purpose

Lossless real-time compression library and CLI (`zstd` / `unzstd`) with tunable compression levels, dictionary support, and architecture-aware optimizations (including x86 SSE and Arm NEON paths in match-finding code).

## Build system

Make (primary/reference). Also CMake and Meson available upstream; Phase 1 evaluation used `make`.

## Dependencies

Debian packages used in evaluation: `build-essential`, `git`, `ca-certificates`, `file` (required by `make check` / `playTests.sh`).

## Test command

```bash
cd /src && make check
```

## Benchmark command

```bash
# Fixed 32 MiB input from upstream datagen; single-thread compress+decompress loop
/src/tests/datagen -g33554432 > /work/input.bin
for i in $(seq 1 N); do
  /src/zstd -f -T1 -6 /work/input.bin -o /work/out.zst
  /src/zstd -f -d /work/out.zst -o /work/out.bin
done
```

Evaluation used `N=20`, level `6`. Final packaged workload targets ~10 s with fewer iterations (same level/input pattern).

## Fixed input

Upstream `datagen -g33554432` → 32 MiB. SHA-256:

`35cafdf130f1db75dbfec226ca9a1e100d38c3e26d8c8651808715de10450235`

## Output verification

1. Compression completes (exit 0).
2. Decompression completes (exit 0).
3. SHA-256 of decompressed bytes must equal original input SHA-256.
4. Compressed `.zst` bytes were bit-identical across repeated runs at fixed level/flags on amd64 (`99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f`).

## AMD64 result

- Docker build result: **passed** (`phase1-eval-zstd:amd64`)
- Test result: **passed** — `make check` exit 0 on three consecutive runs
- Benchmark result: five runs at level 6, 20 iterations (see reliability)
- Output verification result: **passed** (round-trip SHA match every run)

## ARM64 result

- Docker build result: evaluated via Buildx `linux/arm64` (smoke path; full `make check` under QEMU skipped to avoid multi-hour wait)
- Test result: **not tested** under QEMU full suite (amd64 suite verified three times)
- Benchmark execution result: functional smoke compress/decompress under QEMU (timing **not** real Arm performance)
- Output verification result: round-trip correctness checked on smoke path

Clearly: QEMU timing is not real Arm hardware performance.

## Test reliability

| run | passed | failed | skipped | exit code |
|---:|---|---|---|---:|
| 1 | make check OK | 0 | n/a | 0 |
| 2 | make check OK | 0 | n/a | 0 |
| 3 | make check OK | 0 | n/a | 0 |

Reliable: same valid result on all three runs.

## Benchmark reliability

| run | elapsed (s) | exit | output checksum (zst) | correctness |
|---:|---:|---:|---|---|
| 1 | 20.762659 | 0 | 99c06a7b…7a4f | PASS |
| 2 | 20.275492 | 0 | 99c06a7b…7a4f | PASS |
| 3 | 19.933303 | 0 | 99c06a7b…7a4f | PASS |
| 4 | 19.934941 | 0 | 99c06a7b…7a4f | PASS |
| 5 | 21.374969 | 0 | 99c06a7b…7a4f | PASS |

- minimum: 19.933303
- maximum: 21.374969
- mean: 20.456273
- median: 20.275492
- standard deviation: 0.546
- coefficient of variation: **~2.7%** (ideal)

Note: mean ~20 s exceeds the 8–15 s packaging target; final package reduces iteration count to ~10 s without changing algorithm code.

## Determinism

Three identical compressions: identical `.zst` SHA-256. Three decompressions: identical round-trip SHA matching input. **Deterministic.**

## Optimization potential

- Hot loops in `zstd_lazy.c` / `zstd_compress.c` match finding
- Existing SSE2 / NEON vectorized match-mask paths — strong x86↔Arm migration study target
- Huffman / FSE entropy coding
- Memory allocation and buffer reuse
- Single-thread vs multi-thread (`-T`) tradeoffs
- Compiler flags / LTO
- Scalar fallbacks when SIMD disabled

No optimizations implemented in Phase 1.

## Problems and risks

- Annotated tag SHA ≠ peeled commit; must pin peeled commit `f8745da6…`
- `make check` requires `file` package
- High compression levels (e.g. 19) take hundreds of seconds — unsuitable for ~10 s bench
- Full Arm64 `make check` under QEMU is very slow; used functional smoke instead for candidate screening

## Candidate score

| Criterion | Score (1–5) | Evidence |
|---|---:|---|
| Primarily C | 5 | Core library and CLI in C |
| Build simplicity | 5 | Plain `make` |
| Automated test reliability | 5 | `make check` ×3 exit 0 |
| Benchmark reliability | 5 | CV ~2.7% |
| Deterministic output | 5 | Identical zst + round-trip |
| AMD64 compatibility | 5 | Build/test/bench passed |
| ARM64 compatibility | 4 | Image/smoke path; full QEMU suite not run |
| Docker reproducibility | 5 | Clean Debian image build |
| Optimization potential | 5 | SIMD + hot compress paths |

Weighted total: **4.85 × 20 = 97.0 / 100**  
(5×0.10 + 5×0.10 + 5×0.15 + 5×0.15 + 5×0.15 + 5×0.05 + 4×0.10 + 5×0.10 + 5×0.10) × 20 = **97.0**
