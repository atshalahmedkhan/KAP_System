# LZ4

## Repository

- Official URL: https://github.com/lz4/lz4
- Commit SHA: `ebb370ca83af193212df4dcbadcc5d87bc0de2f0`
- Release/tag: `v1.10.0`
- License: **BSD-2-Clause** for `lib/`; **GPL-2.0-or-later** for CLI and tests. Not a single permissive license for the whole tree — document both; do not describe the CLI as BSD-only.
- Primary language: C
- Approximate project size: ~4.7M tree in eval image; ~48 `.c` files; `lib/*.c` ~8.5k LOC

## Purpose

Extremely fast lossless compression (LZ4 block/frame formats) with a CLI (`lz4`) and optional high-compression (HC) mode.

## Build system

Make (also CMake/Meson upstream). Evaluation used `make`.

## Dependencies

`build-essential`, `git`, `ca-certificates`, `python3` (for deterministic input generation in eval harness).

## Test command

```bash
cd /src && make test
```

## Benchmark command

```bash
# 64 MiB seeded synthetic input; HC level -9 compress + decompress loop
lz4 -f -9 /work/input.bin /work/out.lz4
lz4 -f -d /work/out.lz4 /work/out.bin
# repeated 40 times in evaluation
```

## Fixed input

64 MiB LCG-seeded patterned file (`seed=0xC0FFEE42`). SHA-256:

`00915a032b5fcd9e7c96fb9d57582a74bb92fee12d94f99b30d34f00498bdab0`

## Output verification

Decompressed SHA-256 must equal input. Compressed frame SHA was stable on amd64:

`0ed70c27e868ac4cebbc63c29fa10fcb701029a44b81adfba5f818f55663bfe4`

## AMD64 result

- Docker build: **passed**
- Tests: **passed** ×3 (`make test` exit 0)
- Benchmark: five runs ~8.6–13.7 s
- Output verification: **passed** every run

## ARM64 result

- Docker build: **passed** (`phase1-eval-lz4:arm64` via Buildx)
- Full `make test` under QEMU: **not completed** (long-running; interrupted to proceed with packaging)
- Functional smoke compress/decompress under QEMU: used for compatibility check
- QEMU timing is not real Arm performance

## Test reliability

| run | result | exit code |
|---:|---|---:|
| 1 | passed | 0 |
| 2 | passed | 0 |
| 3 | passed | 0 |

## Benchmark reliability

| run | elapsed (s) | correctness |
|---:|---:|---|
| 1 | 12.755831 | PASS |
| 2 | 10.207369 | PASS |
| 3 | 13.652288 | PASS |
| 4 | 10.418685 | PASS |
| 5 | 8.592346 | PASS |

- min 8.592346 / max 13.652288 / mean 11.125304 / median 10.418685
- stdev ~1.833 / **CV ~16.5%** (above 5% preference; cold/warm + FS cache effects)

## Determinism

Compressed and round-trip hashes identical across three runs on amd64. **Deterministic.**

## Optimization potential

- Match finding / literals encoding hot paths
- HC mode CPU cost
- Memory copies and frame I/O
- Limited SIMD relative to zstd/libjpeg-turbo — still optimizable via compiler and algorithmic tweaks
- Threading not central to default CLI path

## Problems and risks

- Dual license (BSD lib + GPL CLI) complicates redistribution narrative
- High benchmark CV on Docker Desktop
- Full Arm64 test suite under QEMU very slow

## Candidate score

| Criterion | Score | Evidence |
|---|---:|---|
| Primarily C | 5 | C library + CLI |
| Build simplicity | 5 | `make` |
| Test reliability | 5 | `make test` ×3 OK |
| Benchmark reliability | 3 | CV ~16.5% |
| Deterministic output | 5 | Stable hashes |
| AMD64 compatibility | 5 | Passed |
| ARM64 compatibility | 3 | Build OK; full tests not finished under QEMU |
| Docker reproducibility | 5 | Clean build |
| Optimization potential | 3 | Less SIMD surface than zstd/LJT |

Weighted total: **4.20 × 20 = 84.0 / 100**
