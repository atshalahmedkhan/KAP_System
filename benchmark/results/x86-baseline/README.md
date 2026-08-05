# x86 baseline results

Provisional benchmark **state 1** evidence. Recorded on the available local
x86_64 Docker Desktop host with the A1 llama.cpp harness.

Issue #12 asks for the shared x86 sudo/SSH host, but no endpoint or access
details are present in the repository. This local run records everything that
could be measured without that access. Re-run on the designated shared host
before treating A4 as complete or this directory as the final comparison
baseline.

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

CV is low enough to trust for this host. It is recorded rather than silently
treated as noise-free; future comparisons must report their own CV and
preserve Arm64 baseline and optimized results in separate state directories.

Files:

- `raw-timings.csv` — all seven measured durations
- `summary.txt` — aggregate statistics and load-gate result
- `correctness.txt` — correctness hash and verification count
- `env-snapshot.txt` — host, container, Docker, workload, and run provenance
