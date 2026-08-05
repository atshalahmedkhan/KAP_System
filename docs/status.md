# Project status

Tracks actual repo state against [revised-plan.md](revised-plan.md) §6.
Update this file whenever a task completes — don't let it drift from the code,
it's the fastest way for an agent (or a human) to know what's real vs. planned.

> **The 21-phase plan in [project-spec.md](project-spec.md) §9/§16 is
> superseded.** See [revised-plan.md](revised-plan.md) — the submission
> deadline is 2026-08-14 16:00 PT and the plan was re-cut on 2026-08-05 to fit
> the remaining nine days. project-spec.md remains the long-term product
> reference.

## Current position: Phase A (Foundation), day 1 of 9

### Planning: ✅ complete (2026-08-05)
- Deadline verified from the Devpost rules page — 9 days remaining
- Benchmark app switched from **zstd → llama.cpp** (hackathon requires an
  AI solution; zstd is a compression library)
- Scope cut to **3 components built deep**, rest specced
- Full rationale and schedule: [revised-plan.md](revised-plan.md)
- Open decisions tracked as wayfinder tickets on the issue tracker

### Phase A — Foundation: not started
- [ ] **A1** llama.cpp benchmark package (Dockerfile, pinned commit + model
      SHA, fixed prompt/seed, output hash, benchmark harness) — *K*
- [ ] **A2** Arm64 server recon (CPU, OS, sudo, Docker, `perf_event_paranoid`)
      — *A* — **highest-risk unknown, day-1 priority**
- [ ] **A3** Python scaffold (`archshift/`, `pyproject.toml`, config, logging) — *K*
- [ ] **A4** x86 baseline recorded (state 1) — *K*

### Phase B — The three components: in progress
- [x] **B1** Profiling Engine — *K* — `perf stat`/`perf record` runner,
      #4-schema parser, Docker Desktop captured unsupported-event fixture, and
      graceful-degradation tests complete. Native Arm profiling remains Phase C.
- [ ] **B2** Optimization Agent — *A*
- [ ] **B3** Verification & Safety Engine — *K*
- [ ] **B4** `archshift run` entrypoint wiring B1→B2→B3 — *K*

### Phase C — Real Arm64 run: not started
- [ ] **C1** Arm64 host ready (Docker, perf, isolation, limits, logging) — *A*
- [ ] **C2** Manual migration documented — *A*
- [ ] **C3** Arm64 baseline recorded (state 2) — *A*
- [ ] **C4** Full loop on Arm64: one accepted optimization (state 3) **and one
      recorded rejection** — *K*

### Phase D — Evidence and submission material: not started
- [ ] **D1** Evidence bundle generator — *K*
- [ ] **D2** Static HTML report — *A*
- [ ] **D3** Demo video (<3 min) — *K + A*
- [ ] **D4** LICENSE (MIT or Apache-2.0), README, Arm64 setup instructions — *A*
- [ ] **D5** Deferred-component design docs in `docs/deferred/` — *K*

### Phase E — Buffer and submit: not started
- [ ] **E1** Slack day
- [ ] **E2** Devpost submission — target Aug 13 evening

## Superseded work

**`phase1-benchmark/` (zstd) has been removed** from the working tree as of the
2026-08-05 replan. zstd is not an AI workload and does not satisfy the
hackathon's eligibility bar. The directory — Dockerfile, benchmark harness,
CV statistics scripts, verification and reproducibility docs — remains in git
history at commit `a44631a` and can be restored with:

```bash
git checkout a44631a -- phase1-benchmark/
```

The benchmark harness pattern (warm-up, N iterations, mean/stdev/CV, expected
output hashing) is worth consulting when building A1.

## Repo layout

```
KAP_System/
├── AGENTS.md                  # agent entry point (Codex / general)
├── CLAUDE.md                  # agent entry point (Claude Code)
├── README.md                  # top-level project README
└── docs/
    ├── revised-plan.md         # ← the operative plan (9-day)
    ├── status.md               # this file
    ├── project-spec.md         # long-term product spec (phases superseded)
    ├── architecture.md         # component diagram
    ├── hackathon.md            # submission requirements, verified dates
    └── deferred/               # design docs for specced-not-built components
```
