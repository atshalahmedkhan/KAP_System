# llama.cpp benchmark package

Pinned CPU-only llama.cpp benchmark for x86_64 and Arm64.

## Locked workload

- llama.cpp commit: `e031d956797f9a10f704fa523fe5fd9b72e9015c`
- model: Qwen2.5-0.5B-Instruct Q4_0, Apache-2.0
- model revision: `9217f5db79a29953eb74d5343926648285ec7e67`
- model SHA-256:
  `7671c0c304e6ce5a7fc577bcb12aba01e2c155cc2efd29b2213c95b18edaf6ed`
- invocation: seed `42`, temperature `0`, `512` maximum generated tokens,
  `$(nproc)` threads

`token-id-runner` emits generated token IDs only. Timing/log text never enters
the correctness artifact. `verify-output.sh` SHA-256 hashes that token stream
and checks an architecture-specific expected value.

## Run

From this directory:

```bash
./run-benchmark.sh
```

The script builds a local image on first use, executes two discarded warm-ups
and seven measured runs, pins each process with `taskset`, lowers its scheduling
priority with `nice`, verifies every generated token-ID stream, then prints
mean, sample standard deviation, and coefficient of variation.

Build both supported targets:

```bash
docker buildx build --platform linux/amd64,linux/arm64 benchmark/llamacpp
```
