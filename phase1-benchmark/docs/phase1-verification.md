# Phase 1 verification (observed results only)

## Environment

| Item | Result |
|---|---|
| Host OS | Windows 10 build 26200 |
| Working directory | KAP_SYSTEM/phase1-benchmark |
| Docker Desktop | 4.81.0 |
| Docker Engine | 29.6.1 |
| Context | desktop-linux (Linux containers) |
| Buildx | v0.35.0-desktop.2 |
| Host arch | x86_64 |
| amd64 probe | verified (`uname -m` = x86_64) |
| arm64/QEMU probe | verified (`uname -m` = aarch64) |

## Selected application

| Field | Value |
|---|---|
| Application | zstd |
| Upstream | https://github.com/facebook/zstd |
| Tag | v1.5.7 |
| Commit | f8745da6ff1ad1e7bab384bd1f9d742439278e99 |
| License | dual BSD OR GPLv2 |

## Fixed input / expected output

| Artifact | Path | Observed |
|---|---|---|
| Input | benchmark/inputs/input.bin | 33554432 bytes |
| Input SHA-256 | benchmark/expected/original-input.sha256 | 35cafdf130f1db75dbfec226ca9a1e100d38c3e26d8c8651808715de10450235 |
| Expected .zst | benchmark/expected/expected-output.zst | present |
| Expected .zst SHA-256 | benchmark/expected/expected-output.sha256 | 99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f |

## Candidate evaluation (amd64) — observed

### Candidate 1 — zstd

| Check | Result |
|---|---|
| Docker build | passed |
| make check run 1 | passed (exit 0) |
| make check run 2 | passed (exit 0) |
| make check run 3 | passed (exit 0) |
| Benchmark ×5 (level 6, 20 iters) | passed; Correctness PASS each run |
| Times (s) | 20.762659, 20.275492, 19.933303, 19.934941, 21.374969 |
| Mean / median / min / max | 20.456273 / 20.275492 / 19.933303 / 21.374969 |
| Stdev / CV | ~0.546 / ~2.7% |
| Determinism | passed (identical .zst + round-trip SHA) |

### Candidate 2 — LZ4

| Check | Result |
|---|---|
| Docker build | passed |
| make test ×3 | passed (exit 0 each) |
| Benchmark ×5 | passed; Correctness PASS |
| Times (s) | 12.755831, 10.207369, 13.652288, 10.418685, 8.592346 |
| Mean / CV | 11.125304 / ~16.5% |
| Arm64 image build | passed |
| Arm64 full make test under QEMU | not completed (interrupted) |

### Candidate 3 — libjpeg-turbo

| Check | Result |
|---|---|
| Docker build | passed |
| ctest ×3 | passed (664/664 each) |
| Benchmark ×5 | passed; Correctness PASS (same-arch) |
| Times (s) | 13.257529, 8.827594, 8.519413, 7.543952, 6.761995 |
| Mean / CV | 8.982097 / ~25% |
| Arm64 full ctest under QEMU | not completed |

## Clean rebuild check — observed

Procedure: removed `phase1-benchmark:amd64` / `phase1-benchmark:arm64` images only; rebuilt from Dockerfile; reran verify and benchmark.

### AMD64

| Step | Result |
|---|---|
| `docker buildx build --platform linux/amd64 --load -t phase1-benchmark:amd64 .` | passed (exit 0) |
| `docker run --rm phase1-benchmark:amd64 verify` | passed — Correctness: PASS |
| Benchmark ×5 (`BENCH_ITERS=10`) | passed — Correctness: PASS each run |

Packaged benchmark times (seconds):

| Run | Elapsed | Correctness | Output SHA-256 |
|---:|---:|---|---|
| 1 | 8.191386 | PASS | 99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f |
| 2 | 8.009837 | PASS | 99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f |
| 3 | 8.222462 | PASS | 99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f |
| 4 | 7.840853 | PASS | 99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f |
| 5 | 8.376938 | PASS | 99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f |

| Stat | Value |
|---|---:|
| minimum | 7.840853 |
| maximum | 8.376938 |
| mean | 8.128295 |
| median | 8.191386 |
| standard deviation | 0.185109 |
| coefficient of variation | 2.28% |

### ARM64 (QEMU)

| Step | Result |
|---|---|
| `docker buildx build --platform linux/arm64 --load -t phase1-benchmark:arm64 .` | passed (exit 0) |
| `docker run --rm --platform linux/arm64 phase1-benchmark:arm64 verify` | passed — Correctness: PASS |
| `docker run --rm --platform linux/arm64 -e BENCH_ITERS=2 phase1-benchmark:arm64 benchmark` | passed — Correctness: PASS |
| Output checksum | 99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f |
| Emulated elapsed (informational only) | 16.064475 s |
| Performance comparison valid | NO |

QEMU timing is not real Arm hardware performance.

### AMD64 `make check` on packaged image

| Context | Result |
|---|---|
| Candidate evaluation (`phase1-eval-zstd:amd64`) ×3 | passed |
| Clean-rebuild packaged image `make check` | started after Arm64 steps; see `benchmark/results/clean-test-amd64.log` when finished |

## Selection

Selected repository: **zstd** (see `docs/benchmark-selection.md`). Weighted score 97.0 vs LZ4 84.0 vs libjpeg-turbo 81.0.

## Remaining blockers

| Item | Status |
|---|---|
| Full Arm64 upstream test suites under QEMU for all three candidates | not completed (time); packaged Arm64 verify+benchmark passed for zstd |
| Phase 2 work | not started (by design) |

## Final status

**Phase 1 benchmark selection is complete**

Observed basis: three candidates evaluated on amd64; zstd selected and pinned; fixed input/expected stored; final Dockerfile builds amd64 and arm64; amd64 clean rebuild verify+benchmark×5 passed (~8.1 s mean, CV 2.28%); arm64 verify+benchmark Correctness PASS under QEMU with performance comparison marked NO.