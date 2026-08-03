# Benchmark selection

## Selected application

**Zstandard (zstd)**

- Category: data compression
- Official repository: https://github.com/facebook/zstd
- Exact pinned commit: `f8745da6ff1ad1e7bab384bd1f9d742439278e99`
- Release tag: `v1.5.7` (annotated tag object `ac66b19e…`; peel to the commit above)
- License: dual **BSD OR GPLv2** — not permissive-only; preserve `LICENSE` and `COPYING`

## Why it satisfies mandatory requirements

| Requirement | Status |
|---|---|
| Primarily C | Yes |
| Compression or image domain | Compression |
| Open-source | Yes |
| CPU/memory intensive | Yes (level-6 compress loops) |
| Automated tests | `make check` |
| Deterministic fixed input | `datagen -g33554432` |
| Builds in Linux Docker | Verified amd64 |
| linux/amd64 build/run | Verified |
| linux/arm64 via Buildx/QEMU | Packaged multi-platform; functional verification in final stage |
| Clear noninteractive benchmark | `docker run … benchmark` |
| ~10 s on x86 configurable | `BENCH_ITERS` / level |
| Optimization opportunities | SIMD match paths, entropy coding, buffers |
| No proprietary / GUI / network at bench time | Yes |
| Pinnable commit/tag | Yes |

## Why appropriate for x86-to-Arm research

Portable C core with existing architecture-specific acceleration (SSE/NEON-related paths in compression). Later phases can compare scalar vs SIMD and study migration risks without rewriting an entire application.

## Why tests are trustworthy

`make check` exited 0 on three consecutive amd64 Docker runs with consistent behavior.

## Why benchmark is trustworthy

Five amd64 timed runs produced CV ~2.7% with identical output checksums and PASS round-trips.

## Why output is deterministic

Fixed `datagen` input; fixed `-T1 -6`; identical compressed SHA across runs; decompressed bytes match input SHA every time.

## Why code can be optimized later

Hot loops, entropy coding, optional SIMD paths, threading knobs, compiler flags — without requiring GUI or proprietary tools.

## Why others were rejected

- **LZ4:** lower research SIMD surface and higher timing CV; still a strong alternate.
- **libjpeg-turbo:** lossy oracle model and unproven cross-arch identity; high CV.

## Current limitations

- Candidate Arm64 full test suites under QEMU were abbreviated (smoke/build focus).
- Packaged iteration count tuned from eval’s ~20 s mean down toward ~10 s.
- QEMU Arm timings must never be treated as hardware performance.

## Risks for later phases

- Dual licensing obligations when redistributing modifications.
- Annotated-tag vs peeled-commit confusion if re-pinning.
- Multi-thread defaults in newer zstd CLIs — keep `-T1` for stable benches.
