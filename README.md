# KAP System — Phase 1 Benchmark Selection

## Status

**Phase 1 is complete.**

This repository contains the completed first phase of an x86-to-Arm migration and optimization research project.

Phase 1 focused only on selecting, evaluating, and packaging a reproducible benchmark.

It did not include:

* Architecture migration analysis
* Native Arm performance optimization
* AI agent implementation
* Source-code optimization
* Automated pull-request creation
* Dashboard development

---

# 1. Phase 1 Goal

The goal of Phase 1 was to:

1. Find real open-source C or C++ applications in compression or image processing.
2. Evaluate three serious candidates inside Docker.
3. Test their reliability, determinism, correctness, and benchmark stability.
4. Select one candidate using measured evidence.
5. Pin the exact source version and commit.
6. Create a reproducible benchmark lasting approximately 8–15 seconds.
7. Verify that the benchmark works on AMD64 and ARM64.
8. Document the entire process for future research phases.

The selected benchmark will later be used for:

* x86-to-Arm migration research
* Arm performance profiling
* SIMD and compiler analysis
* AI-assisted optimization
* Correctness-gated performance experiments

---

# 2. Project Environment

Phase 1 was completed using the following environment:

| Component             | Configuration                   |
| --------------------- | ------------------------------- |
| Host operating system | Windows                         |
| Container runtime     | Docker Desktop Linux containers |
| Docker Desktop        | 4.81.0                          |
| Docker Engine         | 29.6.1                          |
| Docker context        | `desktop-linux`                 |
| Docker Buildx         | v0.35.0-desktop.2               |
| Working directory     | `KAP_SYSTEM`                    |
| AMD64 target          | `linux/amd64`                   |
| ARM64 target          | `linux/arm64` through QEMU      |
| AMD64 verification    | `uname -m` returned `x86_64`    |
| ARM64 verification    | `uname -m` returned `aarch64`   |

Docker Buildx successfully supported both:

```text
linux/amd64
linux/arm64
```

ARM64 execution was performed through QEMU emulation.

QEMU was used only for:

* ARM64 build verification
* Functional execution
* Output correctness
* Round-trip validation

QEMU timings are not treated as native Arm performance measurements.

---

# 3. Repository Structure

All Phase 1 work is located under:

```text
KAP_SYSTEM/phase1-benchmark/
```

Project structure:

```text
phase1-benchmark/
├── README.md
├── Dockerfile
├── .dockerignore
│
├── benchmark/
│   ├── source.lock
│   ├── inputs/
│   │   └── input.bin
│   ├── expected/
│   │   └── expected-output.zst
│   └── results/
│
├── candidates/
│   ├── candidate-1.md
│   ├── candidate-2.md
│   └── candidate-3.md
│
├── container/
│   ├── benchmark.sh
│   ├── test.sh
│   └── verify.sh
│
├── docs/
│   ├── benchmark-selection.md
│   ├── candidate-comparison.md
│   ├── phase1-verification.md
│   └── reproducibility.md
│
└── scripts/
    ├── build-amd64.ps1
    ├── build-arm64.ps1
    ├── benchmark-amd64.ps1
    ├── benchmark-arm64.ps1
    ├── test-amd64.ps1
    ├── verify-amd64.ps1
    └── verify-arm64.ps1
```

The project contains:

* Docker build configuration
* Candidate evaluation reports
* Fixed benchmark inputs
* Expected outputs
* Benchmark result storage
* Linux container scripts
* PowerShell wrapper scripts
* Reproducibility documentation
* Verification documentation

---

# 4. Initial Candidate Pool

The following open-source projects were initially considered:

* zstd
* LZ4
* libjpeg-turbo
* zlib-ng
* brotli
* xz
* libpng
* qoi

The candidate pool was narrowed to three final applications:

1. zstd
2. LZ4
3. libjpeg-turbo

These three were selected for serious evaluation because they offered the strongest combination of:

* Real-world usage
* C or C++ implementation
* Automated upstream testing
* Docker build compatibility
* Repeatable workloads
* Architecture-specific code
* SIMD potential
* Future performance-research value

---

# 5. Final Candidate Set

| Candidate     | Category             | Version | Commit      | License                          |
| ------------- | -------------------- | ------- | ----------- | -------------------------------- |
| zstd          | Lossless compression | v1.5.7  | `f8745da6…` | Dual BSD or GPLv2                |
| LZ4           | Lossless compression | v1.10.0 | `ebb370ca…` | BSD-2-Clause library and GPL CLI |
| libjpeg-turbo | Image compression    | 3.2.0   | `c85e6b90…` | IJG and Modified BSD             |

Source repositories:

```text
https://github.com/facebook/zstd
https://github.com/lz4/lz4
https://github.com/libjpeg-turbo/libjpeg-turbo
```

Each project was pinned to a specific release and commit.

This prevents future upstream changes from silently changing the benchmark.

---

# 6. Candidate Evaluation Method

Each candidate was evaluated using the same general process.

## 6.1 Docker build

For each candidate:

* The source repository was cloned.
* The exact version or commit was checked out.
* The project was built inside Docker.
* Build success or failure was recorded.
* Build-system complexity was evaluated.
* Multi-architecture suitability was reviewed.

## 6.2 Automated testing

The upstream test suite was executed three times for each candidate.

This was done to check:

* Test reliability
* Repeatability
* Build correctness
* Upstream validation quality
* Suitability for future optimization work

## 6.3 Benchmarking

Each candidate benchmark was executed five times.

The evaluation considered:

* Runtime
* Mean time
* Minimum time
* Maximum time
* Standard deviation
* Coefficient of variation
* Warm-up behavior
* Output correctness
* Output determinism
* Future benchmark usefulness

## 6.4 Correctness

Correctness depended on the candidate type.

For lossless compression projects:

* The input was compressed.
* The compressed output was checked.
* The output was decompressed.
* The decompressed bytes were compared with the original input.
* SHA-256 hashes were used for exact verification.

For libjpeg-turbo:

* Exact pixel round-trip equality was not possible because JPEG is lossy.
* Correctness required an output oracle rather than an exact byte comparison.

## 6.5 Architecture suitability

Each project was also reviewed for:

* AMD64 support
* ARM64 support
* Architecture-specific source code
* SIMD implementation
* Compiler behavior
* Docker multi-platform support
* Future optimization potential

---

# 7. Candidate 1 — zstd

## Project

```text
facebook/zstd
```

## Version

```text
v1.5.7
```

## Commit

```text
f8745da6…
```

## Category

Lossless compression

## AMD64 build

```text
PASS
```

## Automated tests

Command:

```bash
make check
```

Runs:

```text
3
```

Result:

```text
3/3 passed
```

## Benchmark evaluation

The earlier candidate-evaluation workload used:

* Compression level 6
* Repeated compression
* Fixed input
* Correctness verification

Observed result:

```text
Mean runtime: approximately 20.5 seconds
Coefficient of variation: approximately 2.7%
```

The final packaged benchmark was later shortened to approximately eight seconds.

## Correctness

zstd produced:

* Deterministic compressed output
* Stable SHA-256 results
* Successful decompression
* Exact lossless round trip
* Original input recovery

## Research potential

zstd provides useful future research areas:

* SIMD implementations
* Architecture-specific hot paths
* Compression kernels
* Memory behavior
* Compiler vectorization
* Arm-specific code paths
* Runtime dispatch
* Native performance profiling

## Candidate assessment

zstd provided:

* The most reliable benchmark
* The lowest timing noise
* The strongest correctness story
* The easiest deterministic verification
* A straightforward Make-based build
* Strong future optimization value

---

# 8. Candidate 2 — LZ4

## Project

```text
lz4/lz4
```

## Version

```text
v1.10.0
```

## Commit

```text
ebb370ca…
```

## Category

Lossless compression

## AMD64 build

```text
PASS
```

## Automated tests

Command:

```bash
make test
```

Runs:

```text
3
```

Result:

```text
3/3 passed
```

## Benchmark evaluation

Observed benchmark range:

```text
Approximately 8.6 to 13.7 seconds
```

Mean:

```text
Approximately 11.1 seconds
```

Coefficient of variation:

```text
Approximately 16.5%
```

## Correctness

LZ4 produced:

* Deterministic compressed output
* Successful decompression
* Exact lossless round trip

## Research potential

LZ4 is:

* Small
* Fast
* Easy to understand
* Easy to build
* Suitable for basic compression research

However, its SIMD and architecture-specific optimization surface was considered weaker than zstd.

## Rejection reason

LZ4 was not selected because:

* Benchmark timing was significantly noisier.
* Small future improvements would be harder to distinguish from normal variation.
* The architecture-optimization surface was less compelling.
* zstd provided a stronger overall research foundation.

---

# 9. Candidate 3 — libjpeg-turbo

## Project

```text
libjpeg-turbo/libjpeg-turbo
```

## Version

```text
3.2.0
```

## Commit

```text
c85e6b90…
```

## Category

Lossy image compression

## AMD64 build

```text
PASS
```

## Automated tests

Test system:

```text
CTest
```

Tests per run:

```text
664
```

Runs:

```text
3
```

Result:

```text
664/664 passed in all three runs
```

## Benchmark evaluation

Observed benchmark range:

```text
Approximately 6.8 to 13.3 seconds
```

Coefficient of variation:

```text
Approximately 25%
```

A strong warm-up effect was observed.

## Correctness

JPEG compression is lossy.

This means:

* Decompressed pixels do not exactly match original pixels.
* Exact SHA-based round-trip verification cannot be used.
* A quality metric or output oracle is required.
* Cross-architecture correctness is harder to prove.

## Research potential

libjpeg-turbo had the strongest visible SIMD story.

It includes opportunities related to:

* Vectorized image processing
* Assembly routines
* Architecture-specific implementations
* CPU instruction-set optimization

## Rejection reason

libjpeg-turbo was not selected because:

* It had the highest benchmark variation.
* Warm-up effects reduced benchmark reliability.
* Lossy output weakened exact correctness verification.
* Cross-architecture result comparison was more complicated.
* It was less suitable for the strict Phase 1 correctness requirement.

---

# 10. Weighted Candidate Scores

Final weighted scores:

| Candidate     | Score |
| ------------- | ----: |
| zstd          |  97.0 |
| LZ4           |  84.0 |
| libjpeg-turbo |  81.0 |

The weighted evaluation considered:

* Build reliability
* Upstream test reliability
* Benchmark stability
* Determinism
* Correctness strength
* Docker packaging
* Licensing
* ARM64 compatibility
* Future optimization potential
* SIMD and architecture research value

---

# 11. Final Selection

## Selected application

```text
zstd
```

## Selected version

```text
v1.5.7
```

## Selected commit

```text
f8745da6…
```

Selection documentation:

```text
docs/candidate-comparison.md
docs/benchmark-selection.md
benchmark/source.lock
```

## Why zstd was selected

zstd was selected because it had:

* The highest weighted score
* Reliable automated tests
* Low timing variation
* Deterministic compressed output
* Exact lossless round-trip verification
* A simple Make-based build system
* Strong Docker reproducibility
* Useful SIMD and architecture-specific code
* Strong future optimization potential

## Why LZ4 was rejected

LZ4 was rejected because:

* Its benchmark CV was approximately 16.5%.
* Its timing was too noisy for detecting smaller performance changes.
* Its SIMD research surface was less compelling.

## Why libjpeg-turbo was rejected

libjpeg-turbo was rejected because:

* Its benchmark CV was approximately 25%.
* It had a strong warm-up effect.
* JPEG output is lossy.
* Exact output round-trip validation was not possible.
* Cross-architecture correctness was harder to demonstrate.

---

# 12. Final Packaged Benchmark

The final benchmark uses:

```text
zstd v1.5.7
```

Docker image tags:

```text
phase1-benchmark:amd64
phase1-benchmark:arm64
```

The Dockerfile:

1. Clones the pinned zstd source.
2. Checks out the locked release and commit.
3. Builds zstd using Make.
4. Includes the fixed benchmark input.
5. Includes the expected compressed output.
6. Includes checksum files.
7. Includes test, verification, and benchmark scripts.
8. Uses a non-root runtime user.
9. Requires no network access during benchmark execution.

---

# 13. Fixed Benchmark Input

Input path:

```text
benchmark/inputs/input.bin
```

Input size:

```text
32 MiB
```

Input SHA-256:

```text
35cafdf130f1db75dbfec226ca9a1e100d38c3e26d8c8651808715de10450235
```

The fixed input ensures that every run processes the exact same data.

---

# 14. Expected Output

Expected compressed output:

```text
benchmark/expected/expected-output.zst
```

Expected output SHA-256:

```text
99c06a7bc00410c4a6a75a3f7d88ca02b229b18d099dccb285d37c4aa2427a4f
```

The expected output is used to verify deterministic compressed bytes.

The benchmark also decompresses the result and confirms that it exactly matches the original input.

---

# 15. Final Benchmark Workload

The packaged workload performs:

* 10 repeated compression and decompression iterations
* zstd compression level 6
* Single-threaded execution using `-T1`
* Fixed 32 MiB input
* Expected output hash checking
* Exact lossless round-trip verification

Expected runtime on the Phase 1 AMD64 development machine:

```text
Approximately 8 seconds
```

Target runtime:

```text
8–15 seconds
```

---

# 16. Correctness Rules

A benchmark result is valid only when correctness passes.

Correctness requires:

1. Compression completes successfully.
2. The compressed output matches the expected SHA when checked.
3. Decompression completes successfully.
4. The decompressed bytes match the original input.
5. The original input SHA remains unchanged.

The scripts report:

```text
Correctness: PASS
```

or:

```text
Correctness: FAIL
```

A timing result must not be accepted when correctness fails.

---

# 17. Build Commands

Run all commands from:

```text
KAP_SYSTEM/phase1-benchmark/
```

## Build AMD64

```bash
docker buildx build \
  --platform linux/amd64 \
  --load \
  -t phase1-benchmark:amd64 \
  .
```

## Build ARM64

```bash
docker buildx build \
  --platform linux/arm64 \
  --load \
  -t phase1-benchmark:arm64 \
  .
```

PowerShell wrapper scripts are available under:

```text
scripts/
```

---

# 18. Test Commands

## Run AMD64 test mode

```bash
docker run --rm phase1-benchmark:amd64 test
```

The candidate evaluation also ran:

```bash
make check
```

three times successfully for zstd.

## ARM64 test note

The complete upstream `make check` suite was not completed under QEMU because it was too slow.

The selected ARM64 package was still validated using:

* Image build
* Functional verification
* Compression
* Decompression
* Expected output SHA
* Exact round-trip comparison

---

# 19. Verification Commands

## Verify AMD64

```bash
docker run --rm phase1-benchmark:amd64 verify
```

## Verify ARM64 through QEMU

```bash
docker run --rm \
  --platform linux/arm64 \
  phase1-benchmark:arm64 \
  verify
```

Expected result:

```text
Correctness: PASS
```

---

# 20. Benchmark Commands

## Benchmark AMD64

```bash
docker run --rm phase1-benchmark:amd64 benchmark
```

## Benchmark ARM64 through QEMU

```bash
docker run --rm \
  --platform linux/arm64 \
  phase1-benchmark:arm64 \
  benchmark
```

The ARM64 benchmark command confirms functional execution and correctness.

It does not provide a valid native Arm performance comparison.

---

# 21. Clean Rebuild Verification

The final Docker images were removed and rebuilt from the Dockerfile.

This confirmed that the project did not depend on hidden local container state.

## AMD64 clean rebuild result

* Build: passed
* Verification: passed
* Benchmark runs: 5
* Correctness failures: 0

Observed benchmark times:

| Run |  Seconds |
| --: | -------: |
|   1 | 8.191386 |
|   2 | 8.009837 |
|   3 | 8.222462 |
|   4 | 7.840853 |
|   5 | 8.376938 |

Final statistics:

| Statistic                |              Result |
| ------------------------ | ------------------: |
| Minimum                  |    7.840853 seconds |
| Maximum                  |    8.376938 seconds |
| Mean                     |    8.128295 seconds |
| Median                   |    8.191386 seconds |
| Standard deviation       |    0.185109 seconds |
| Coefficient of variation | approximately 2.28% |

All five runs returned:

```text
Correctness: PASS
```

## Result interpretation

The benchmark is considered stable because:

* All runs were correct.
* Runtime stayed close to eight seconds.
* Variation was low.
* The workload remained inside the 8–15 second target.
* The coefficient of variation was approximately 2.28%.

---

# 22. ARM64 QEMU Verification

The ARM64 image was successfully:

* Built for `linux/arm64`
* Loaded through Docker Buildx
* Executed using QEMU
* Verified using the fixed benchmark input
* Compared against the expected output
* Decompressed successfully
* Compared against the original input

ARM64 results:

| Check                 | Result  |
| --------------------- | ------- |
| ARM64 build           | Passed  |
| ARM64 verify          | Passed  |
| Output SHA            | Matched |
| Round-trip comparison | Passed  |
| Benchmark correctness | Passed  |

The benchmark explicitly reports:

```text
Performance comparison valid: NO
```

## Why ARM64 QEMU timing is invalid

QEMU emulates ARM64 instructions on an AMD64 host.

It can verify:

* Compatibility
* Execution
* Correctness
* Architecture support

It cannot reliably measure:

* Native Arm execution time
* Cache behavior
* SIMD performance
* Pipeline behavior
* Energy efficiency
* Native AMD64-versus-ARM64 speed

No native Arm performance claim is made in Phase 1.

---

# 23. Reproducibility Controls

The benchmark includes the following reproducibility controls.

## Source pinning

The exact release and commit are recorded in:

```text
benchmark/source.lock
```

## Fixed input

The same 32 MiB input is used for every benchmark run.

## Input checksum

The input SHA-256 is documented.

## Expected output

The expected compressed output is stored in the repository.

## Output checksum

The expected output SHA-256 is documented.

## Docker build

Build dependencies are installed inside Docker.

## Non-root runtime

The container runs the workload using a non-root user.

## Offline execution

No network connection is required during benchmark execution.

## Multiple benchmark runs

The final AMD64 benchmark was executed five times.

## Stored results

Results are stored under:

```text
benchmark/results/
```

## Explicit limitations

QEMU performance limitations and abbreviated ARM64 upstream testing are documented.

---

# 24. Documentation Created

The repository contains the following documentation.

## `README.md`

Contains:

* Project overview
* Phase 1 scope
* Environment
* Commands
* Candidate results
* Benchmark results
* Current status

## `docs/candidate-comparison.md`

Contains:

* Side-by-side candidate analysis
* Measured results
* Strengths
* Weaknesses
* Weighted scoring

## `docs/benchmark-selection.md`

Contains:

* Final zstd selection
* Selection reasoning
* Rejection reasoning
* Research justification

## `docs/reproducibility.md`

Contains:

* Required environment
* Build steps
* Test steps
* Benchmark steps
* Verification steps
* Source-lock information

## `docs/phase1-verification.md`

Contains:

* Observed build results
* Test outcomes
* Benchmark timing
* Correctness results
* AMD64 statistics
* ARM64 functional validation
* Known limitations

## Candidate reports

```text
candidates/candidate-1.md
candidates/candidate-2.md
candidates/candidate-3.md
```

These contain the detailed evaluation for:

* zstd
* LZ4
* libjpeg-turbo

---

# 25. What Was Intentionally Not Done

The following tasks were intentionally excluded from Phase 1.

## No Phase 2 migration analysis

Phase 1 did not inspect:

* x86-only dependencies
* x86 assembly
* Unsupported precompiled binaries
* Incompatible Docker images
* Architecture-specific build failures
* Migration requirements

## No native Arm performance testing

ARM64 was executed through QEMU.

A native Arm machine such as AWS Graviton will be required for real performance measurements.

## No performance profiling

Phase 1 did not collect:

* CPU hotspots
* Cache misses
* Memory latency
* Branch behavior
* Instruction mix
* SIMD utilization
* Compiler vectorization data

## No code optimization

No changes were made to improve:

* Compression speed
* Memory usage
* SIMD behavior
* Compiler output
* Algorithm performance

## No AI agent

Phase 1 does not contain an AI system that:

* Scans repositories
* Finds migration problems
* Generates patches
* Analyzes build failures
* Profiles bottlenecks
* Proposes optimizations

## No self-healing loop

The project does not yet automatically:

* Generate a change
* Build the change
* Run tests
* Benchmark the change
* Accept or reject it
* Roll it back
* Retry

## No automated pull request

Git initialization, commits, branches, pushes, and pull requests are handled separately by the repository owner.

## No dashboard

A dashboard was not required for Phase 1.

## No full ARM64 upstream test suites for all candidates

Full QEMU test suites were abbreviated because they were too slow.

This does not change the final Phase 1 result because:

* All candidates were seriously evaluated on AMD64.
* The selected zstd image built for ARM64.
* ARM64 functional correctness passed.
* ARM64 output SHA matched.
* ARM64 round-trip validation passed.

---

# 26. Phase 1 Completion Checklist

## Environment

* [x] Docker Desktop configured
* [x] Linux containers verified
* [x] Docker Engine verified
* [x] Docker Buildx verified
* [x] AMD64 execution verified
* [x] ARM64/QEMU execution verified

## Candidate discovery

* [x] Initial candidates identified
* [x] Candidate list narrowed to three
* [x] Versions pinned
* [x] Commits pinned
* [x] Licenses reviewed

## Candidate evaluation

* [x] zstd built on AMD64
* [x] LZ4 built on AMD64
* [x] libjpeg-turbo built on AMD64
* [x] zstd tests run three times
* [x] LZ4 tests run three times
* [x] libjpeg-turbo tests run three times
* [x] Candidate benchmarks run
* [x] Determinism checked
* [x] Round-trip correctness checked
* [x] Benchmark reliability evaluated
* [x] Optimization potential evaluated

## Candidate selection

* [x] Weighted scores calculated
* [x] zstd selected
* [x] LZ4 rejection documented
* [x] libjpeg-turbo rejection documented
* [x] Selection report written
* [x] Source locked

## Benchmark packaging

* [x] Dockerfile created
* [x] Fixed input created
* [x] Input SHA recorded
* [x] Expected output created
* [x] Output SHA recorded
* [x] Test script created
* [x] Benchmark script created
* [x] Verification script created
* [x] PowerShell wrappers created
* [x] Non-root execution configured
* [x] Runtime network dependency removed

## Final AMD64 verification

* [x] Clean image rebuild completed
* [x] Verification passed
* [x] Five benchmark runs completed
* [x] All benchmark correctness checks passed
* [x] Statistics calculated
* [x] Runtime target confirmed
* [x] Low benchmark variation confirmed

## Final ARM64 verification

* [x] ARM64 image built
* [x] ARM64 image executed
* [x] ARM64 verification passed
* [x] ARM64 output SHA matched
* [x] ARM64 round trip passed
* [x] QEMU timing marked invalid for performance comparison

## Documentation

* [x] README written
* [x] Candidate reports written
* [x] Candidate comparison written
* [x] Benchmark selection written
* [x] Reproducibility guide written
* [x] Verification report written
* [x] Source lock created
* [x] Result storage created

---

# 27. Current Status

```text
Phase 0 — Project definition: COMPLETE
Phase 1 — Benchmark selection and packaging: COMPLETE
Phase 2 — Architecture and migration analysis: NOT STARTED
Phase 3 — Native Arm profiling and optimization: NOT STARTED
Phase 4 — AI agent automation: NOT STARTED
```

Phase 1 should now be treated as a locked and completed baseline.

---

# 28. Phase 1 Final Deliverable

The completed Phase 1 deliverable contains:

* Three seriously evaluated open-source projects
* A documented weighted comparison
* A technically justified winner
* Pinned zstd source
* Fixed benchmark input
* Expected compressed output
* SHA-256 correctness controls
* AMD64 Docker image
* ARM64 Docker image
* Approximately eight-second workload
* Stable AMD64 benchmark results
* ARM64 functional verification
* Reproducibility scripts
* Verification scripts
* Candidate reports
* Selection documentation
* Explicit limitations

---

# 29. Final Phase 1 Result

The final benchmark uses:

```text
zstd v1.5.7
```

Pinned commit:

```text
f8745da6…
```

Final AMD64 benchmark mean:

```text
8.128295 seconds
```

Final AMD64 coefficient of variation:

```text
Approximately 2.28%
```

AMD64 correctness:

```text
PASS
```

ARM64/QEMU correctness:

```text
PASS
```

Native Arm performance comparison:

```text
NOT PERFORMED
```

Final status:

```text
PHASE 1 COMPLETE
```

---

# 30. Summary

Phase 1 successfully established a reliable and reproducible benchmark foundation for future x86-to-Arm migration and optimization research.

zstd was selected after measured comparison against LZ4 and libjpeg-turbo.

The final benchmark:

* Uses a pinned real-world open-source C project
* Builds for AMD64
* Builds for ARM64
* Uses a fixed 32 MiB input
* Produces a locked expected output
* Verifies exact lossless correctness
* Runs in approximately eight seconds
* Has low timing variation
* Requires no network at benchmark time
* Is fully documented
* Is ready to support the next project phase

**Phase 1 benchmark selection and packaging is complete.**
