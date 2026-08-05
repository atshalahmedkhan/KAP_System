# x86 baseline results

Preserved benchmark **state 1**. Recorded on the local x86_64 Docker Desktop
host with the A1 llama.cpp harness.

- Workload: seed `42`, temperature `0`, `512` generated tokens, `16`
  threads (`nproc`)
- Noise controls: process pinned to CPU `0` with `taskset`, nice level `10`,
  and a pre-run 1-minute load-average gate of `<= 1.0`
- Warm-up: 2 discarded iterations
- Measured: 7 iterations
- Mean: `8.797922 s`
- Sample standard deviation: `0.090861 s`
- CV: `1.03%`
- Token-ID SHA-256:
  `6fffb8546a4a6b4eaec4b86f75d179a1d8bad1a496dc5ff96ddddca40a6d033a`

CV is low enough to trust for this baseline. It is recorded rather than
silently treated as noise-free; future comparisons must report their own CV
and preserve Arm64 baseline and optimized results in separate state
directories.

Files:

- `raw-timings.csv` — all seven measured durations
- `summary.txt` — aggregate statistics and load-gate result
- `correctness.txt` — correctness hash and verification count
- `env-snapshot.txt` — host, container, Docker, workload, and run provenance
