# libjpeg-turbo

## Repository

- Official URL: https://github.com/libjpeg-turbo/libjpeg-turbo
- Commit SHA: `c85e6b905bf237038faa936dab160ebfc5da0344`
- Release/tag: `3.2.0`
- License: IJG + Modified (3-clause) BSD — BSD-style / permissive family; not copyleft. See upstream LICENSE.md.
- Primary language: C (+ SIMD asm/intrinsics under simd/)
- Approximate project size: ~42M tree in eval image; ~272 .c files

## Purpose

High-performance JPEG codec with SIMD acceleration for compress/decompress on x86 and Arm.

## Build system

CMake (cmake + cmake --build + ctest).

## Dependencies

build-essential, cmake, git, ca-certificates, nasm (x86), python3 (eval harness).

## Test command

```bash
cd /src/build && ctest --output-on-failure
```

Observed: 664/664 passed (~411 s wall on amd64 per full run).

## Benchmark command

```bash
cjpeg -dct int -quality 90 -outfile out.jpg input.ppm
djpeg -dct int -ppm -outfile out.ppm out.jpg
# looped 25 times in evaluation on 4000x3000 PPM
```

## Fixed input

Deterministic P6 PPM 4000x3000. SHA-256: bfe0d0e896f7ee31c7ad569e1609dd8df3dcd3fd7f85f95e10e7b7e7ad934459

Fixed JPEG SHA (amd64, int DCT, q90): a5475f614c2deb2a0637238983596149142b1ba482f0d53dbf44071e561afa01

Oracle decompressed PPM SHA: 77101bee885a0073df6558b3cba1ec83ea3eafbcb3b8cc55df42c13c971460b0

## Output verification

Same-arch JPEG and oracle PPM hashes stable across three runs (PASS). Cross-arch bit-identity not fully proven in Phase 1.

## AMD64 result

- Docker build: passed
- Tests: passed x3 (664/664 each)
- Benchmark: five runs ~6.8-13.3 s
- Verification: passed

## ARM64 result

- Full QEMU ctest suite: not completed (too long under emulation)
- Arm64 Buildx image/smoke: see results logs
- QEMU timing is not real Arm performance

## Test reliability

| run | passed | failed | exit |
|---:|---:|---:|---:|
| 1 | 664 | 0 | 0 |
| 2 | 664 | 0 | 0 |
| 3 | 664 | 0 | 0 |

## Benchmark reliability

| run | elapsed (s) | correctness |
|---:|---:|---|
| 1 | 13.257529 | PASS |
| 2 | 8.827594 | PASS |
| 3 | 8.519413 | PASS |
| 4 | 7.543952 | PASS |
| 5 | 6.761995 | PASS |

mean 8.982 / median 8.519 / min 6.762 / max 13.258 / CV ~25%

## Determinism

On amd64 with -dct int: deterministic. Cross-arch identity not established here.

## Optimization potential

Extensive SSE/AVX vs NEON SIMD — strongest migration study surface. DCT/IDCT, color conversion, Huffman. JSIMD_FORCENONE for A/B studies.

## Problems and risks

Lossy codec (oracle JPEG required). Possible cross-arch SIMD differences. Large test suite slow under QEMU. High timing CV without warm-up.

## Candidate score

| Criterion | Score | Evidence |
|---|---:|---|
| Primarily C | 5 | C + asm SIMD |
| Build simplicity | 4 | CMake + nasm |
| Test reliability | 5 | 664/664 x3 |
| Benchmark reliability | 2 | CV ~25% |
| Deterministic output | 4 | Same-arch yes; cross-arch unproven |
| AMD64 compatibility | 5 | Passed |
| ARM64 compatibility | 3 | Full suite not completed under QEMU |
| Docker reproducibility | 4 | Works; heavier deps |
| Optimization potential | 5 | Best SIMD migration story |

Weighted total: 81.0 / 100
