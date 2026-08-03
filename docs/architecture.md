# Architecture overview

Condensed view of [project-spec.md](project-spec.md) §7–8 for quick
reference. Read the full spec before making structural changes.

## Components

```
┌─────────────────┐
│  Web Dashboard   │  connect repo, configure, view all results, open PR
└────────┬─────────┘
         │
┌────────▼─────────┐
│ Repository Scanner│  detect x86-specific issues → compatibility report
└────────┬─────────┘
         │
┌────────▼─────────┐
│  Migration Agent  │  plan → limited patches (Docker, deps, CI, build)
└────────┬─────────┘
         │
┌────────▼─────────┐
│   Build Runner    │  clone → isolated branch → build x86 + Arm64
└────────┬─────────┘
         │
┌────────▼─────────┐
│Correctness Validator│ unit/integration tests, output diff, crash detection
└────────┬─────────┘
         │
┌────────▼─────────┐
│Benchmarking Engine │ exec time, throughput, CPU/mem, image size, variance
└────────┬─────────┘
         │
┌────────▼─────────┐
│ Profiling Engine   │ hotspots, cache misses, stalls, vectorization
└────────┬─────────┘
         │
┌────────▼─────────┐
│ Optimization Agent │ one focused patch from profiling evidence
└────────┬─────────┘
         │
┌────────▼─────────┐
│Safety/Rollback Engine│ attempt limits, auto-rollback, rejection logging
└────────┬─────────┘
         │
┌────────▼─────────┐
│ GitHub Integration │ branch, commits, PR with full evidence bundle
└──────────────────┘
```

## End-to-end workflow

```
connect repo
  → clone
  → x86 baseline build + test
  → compatibility scan
  → migration plan
  → migration patch
  → Arm64 build
  → correctness tests            ─┐
      │ fail → analyze, retry  ◄──┘ (max 3 attempts)
      │ pass
  → unoptimized Arm benchmark
  → profiling
  → optimization patch
  → correctness tests again
  → performance benchmark again
  → accept or reject (see scoring rules, project-spec.md §13)
  → verified results → pull request
```

## Three preserved states (never conflate these)

1. **Original x86 application** — untouched baseline
2. **Migrated, unoptimized Arm64 application** — proves migration alone
3. **Optimized Arm64 application** — proves the optimization's specific delta

Every benchmark report should be attributable to exactly one of these three.

## Safety invariant

No code change reaches a PR without: running on a temp branch, passing
tests, passing a benchmark that beats baseline beyond the noise threshold.
Any failure at any stage triggers rollback, not a "best effort" patch. Full
rules: [project-spec.md](project-spec.md) §12.
