# ArchShift — 9-Day Hackathon Plan (revised 2026-08-05)

**This document supersedes the 21-phase plan in [project-spec.md](project-spec.md)
§9/§16.** That plan describes months of work. The submission deadline is
**2026-08-14 16:00 PT** — nine days from this revision. Everything below is
scoped to that.

The original spec remains the reference for *what ArchShift eventually is*.
This document is the reference for *what we ship by Aug 14*.

---

## 1. What changed, and why

| Area | Original spec | Revised | Reason |
|---|---|---|---|
| Benchmark app | zstd v1.5.7 | **llama.cpp + small quantized LLM** | Hackathon rules require an **AI solution**. zstd is a compression library — off-thesis and arguably ineligible. |
| AI framing | Agent optimizes generic C/C++ | Agent (AI) optimizes an **AI inference workload** | Both halves are AI. Strongest read of the eligibility bar. |
| Scope | 10 components, full autonomy | **3 components built deep**, remainder specced | 75 person-hours. A thin-but-complete chain was the alternative; we chose depth. |
| Phase order | 21 sequential phases | 5 compressed phases (A–E) | Sequential phase gating does not fit a 9-day window. |
| Deadline data | "conflicting, re-verify" | Verified from Devpost rules page | See §7. |

`phase1-benchmark/` (zstd) has been removed from the working tree. It remains
in git history at commit `a44631a` if the benchmark harness scripts are wanted
back.

---

## 2. Destination

> A working, demonstrable **profiling-guided optimization loop** that takes
> llama.cpp inference running on Arm64, profiles it on real Arm hardware,
> generates one optimization via an LLM agent, and **accepts or rejects that
> change on measured evidence** — with the rejection path demonstrated, not
> just claimed.

Submitted to Devpost, Cloud AI track, with public repo, setup instructions,
evidence bundle, and demo video.

## 3. What we build vs. what we spec

### Built (the three)

| # | Component | What it does |
|---|---|---|
| 1 | **Profiling Engine** | Runs `perf stat` / `perf record` against the Arm64 container, parses output into structured JSON: hotspot functions, cache miss rates, IPC, branch mispredicts, instruction mix. This is the evidence that makes it not an LLM wrapper. |
| 2 | **Optimization Agent** | Consumes profile JSON + relevant source/build context. Calls `claude-opus-5` with structured output. Emits: one patch, a stated hypothesis, and an expected-impact estimate. |
| 3 | **Verification & Safety Engine** | Applies the patch on a temp branch. Builds. Runs correctness checks. Benchmarks N iterations. Accepts only if correctness holds **and** improvement clears the noise threshold. Otherwise rolls back and logs the rejection with its reason. |

### Specced, not built (documented in `docs/deferred/`)

Repository Scanner · Migration Agent · Build Runner · GitHub PR automation ·
Web dashboard · Multi-workload support.

Each gets a design doc precise enough that a later session (or a teammate with
spare hours) can pick it up. If time appears, these are the pickup queue in
roughly that order.

---

## 4. Target workload: llama.cpp

**Why llama.cpp**

- C/C++, CPU-only, no GPU — matches the original spec's app constraints (§5)
- Recognisably an AI workload to judges
- Deterministic under fixed seed + `--temp 0` + fixed `--n-predict`
- Real, well-known Arm64 optimization surface: `-mcpu=native`, `+dotprod`,
  `+i8mm`, NEON/SVE kernels, Q4_0 runtime repacking
- A naive Arm64 build leaves substantial measurable performance unused —
  which is exactly what a real migration hits, so the win is honest, not staged

**Pinning requirements** (Phase A deliverable)

- llama.cpp pinned to an exact commit SHA
- Model pinned by filename **and** SHA-256 (small quantized model — TinyLlama
  or Qwen2.5-0.5B class, Q4_0)
- Fixed prompt file, fixed `--seed`, `--temp 0`, fixed `--n-predict`
- Expected output token stream hashed and stored

### Correctness definition — read this carefully

Cross-architecture bit-exact float output is **not** guaranteed. x86 and Arm64
differ in FMA contraction, SIMD reduction order, and libm implementations.
A naive "hash must match across architectures" check will fail for reasons
unrelated to migration bugs.

So correctness is defined in tiers:

| Comparison | Bar |
|---|---|
| **Arm baseline vs. Arm optimized** | **Exact output-hash match required.** Same architecture, same binary layout class — any divergence is a real bug. This is the bar the Verification Engine enforces on every optimization. |
| **x86 baseline vs. Arm baseline** | llama.cpp's own test suite passes on both (`test-backend-ops`, `test-tokenizer-*`), **and** generated text is compared for semantic equivalence. Divergence is reported, not silently accepted. |

The Verification Engine's accept/reject gate operates on the first row. The
second row is migration evidence for the writeup.

## 5. Three preserved states

Unchanged from spec §7/architecture.md — do not conflate these:

1. **x86 baseline** — llama.cpp on the x86 host, untouched
2. **Arm64 baseline** — migrated, unoptimized
3. **Arm64 optimized** — after the accepted optimization

Every benchmark result is tagged with exactly one.

---

## 6. Schedule

Two people, ~75 person-hours total. **K** = Kritarth, **A** = teammate.

### Phase A — Foundation (Aug 5–6)

| ID | Task | Owner | Blocks |
|---|---|---|---|
| A1 | llama.cpp benchmark package: Dockerfile (amd64 + arm64), pinned commit + model SHA, fixed prompt/seed, output hash, benchmark harness (warm-up + N iters + mean/stdev/CV) | K | everything |
| A2 | **Arm64 server recon**: CPU model, core count, OS/kernel, sudo?, Docker?, `perf_event_paranoid` value, shared or dedicated | A | C1, and Profiling Engine feasibility |
| A3 | Python scaffold: `archshift/` package, `pyproject.toml`, config loading, structured logging | K | B1–B3 |
| A4 | Record x86 baseline (state 1) using A1 harness, with `taskset` pin + `nice` + loadavg gate | K | comparison data |

**A2 is the single highest-risk unknown.** If `perf_event_paranoid` is locked
and root is unavailable on the school Arm server, the Profiling Engine — one
of three deliverables — cannot run there. Contingency in §8.

### Phase B — The three components (Aug 6–9)

Built and unit-tested on x86. None of these need Arm hardware to develop.

| ID | Task | Owner |
|---|---|---|
| B1 | **Profiling Engine**: `perf` invocation wrapper, output parser → JSON schema. Unit-tested against recorded fixture `perf` output. | K |
| B2 | **Optimization Agent**: prompt design, `claude-opus-5` structured-output call, patch emission, hypothesis + expected-impact fields. Tested with fixture profile JSON. | A |
| B3 | **Verification & Safety Engine**: temp-branch apply, build, correctness check, benchmark, accept/reject, rollback, rejection log. | K |
| B4 | Wire B1→B2→B3 into a single `archshift run` entrypoint | K |

### Phase C — Real Arm64 run (Aug 9–11)

| ID | Task | Owner |
|---|---|---|
| C1 | Arm64 host ready: Docker, perf access, isolated per-run workspace, timeouts, resource limits, failed-run logging | A |
| C2 | **Manual migration** of the llama.cpp package to Arm64, fully documented — every command, every failure, every fix. This doc is the raw material for the deferred Migration Agent spec. | A |
| C3 | Record Arm64 baseline (state 2) | A |
| C4 | Run the full loop on Arm64. Capture the accepted optimization (state 3) **and at least one rejected attempt**. | K |

**C4 must produce a rejection.** If the agent's first patch is accepted,
deliberately feed it a known-bad or known-slow patch to exercise and record the
rollback path. The rejection is a headline deliverable, not a failure.

### Phase D — Evidence and submission material (Aug 11–13)

| ID | Task | Owner |
|---|---|---|
| D1 | Evidence bundle generator: three states, profile JSON, patch diff, hypothesis, before/after numbers with CV, accept/reject decisions with reasons | K |
| D2 | Static HTML report rendering the evidence bundle (charts: before/after, cache-miss delta, rejection log). No dashboard framework — a generated report page. | A |
| D3 | Demo video, under 3 minutes | K + A |
| D4 | `LICENSE` (MIT or Apache-2.0), README rewrite, Arm64 setup instructions | A |
| D5 | Deferred-component design docs in `docs/deferred/` | K |

### Phase E — Buffer and submit (Aug 13–14)

| ID | Task | Owner |
|---|---|---|
| E1 | Slack day — overrun absorption | both |
| E2 | Devpost submission: description, repo link, setup instructions, video | K |

**Submit by Aug 13 evening.** Treat Aug 14 as emergency margin only.

---

## 7. Hackathon facts (verified 2026-08-05 from the Devpost rules page)

- Submission window: **2026-06-10 09:00 PT → 2026-08-14 16:00 PT**
- Judging: 2026-08-17 → 2026-09-04 · Winners announced ~2026-09-15
- Track: **Cloud AI** (Track 2) — migration/adoption value, source code required
- Judging: Technological Implementation 40 · WOW 25 · Potential Impact 20 · UX/DX 15
- Required: public repo, **MIT or Apache-2.0**, description, Arm64 setup
  instructions. Video optional but strongly recommended.
- **No restriction on cloud provider, infrastructure vendor, or paid services.**
- Free **Arm Developer Program** account signup is required.
- Work must be original and solely owned by the entrant; no projects developed
  under contract with, or with prior financial support from, Arm.

## 8. Risks

| Risk | Impact | Response |
|---|---|---|
| Arm server blocks `perf` (`perf_event_paranoid`, no root) | Kills 1 of 3 deliverables | Detect in A2, day 1. Fallback: rent an AWS Graviton `c7g.xlarge` (~$0.145/hr, ~$10–25 for the window) with root. Rules permit paid infrastructure. |
| Arm server specs unknown until A2 lands | Blocks C1–C4 | A2 is day-1 priority, owner A. Escalate to the Graviton fallback if not resolved by Aug 7. |
| Cross-arch float divergence breaks correctness check | False rejections | Tiered correctness definition, §4. Accept/reject gate compares Arm-to-Arm only. |
| Optimization delta lost in noise on a shared x86 host | Unreliable numbers | `taskset` core pin + `nice` + pre-run loadavg gate + CV-based discard. Arm runs on a quieter host where possible. |
| Agent's first patch is accepted, no rejection demoed | Loses the headline claim | C4 mandates injecting a bad patch to exercise rollback. |
| Scope creep back toward the 21-phase plan | Nothing ships | This document is the scope. Deferred components stay in `docs/deferred/`. |

## 9. Non-negotiables (carried from spec §12)

- Every change on a temporary branch. Every patch stored and reviewable.
- Tests after every patch. Benchmarks after every *valid* patch.
- Incorrect change → rollback. Slower change → rollback.
- Every rejection logged with its reason. Rejections are evidence, not noise.
- The agent explains the reason for every change it proposes.

## 10. Tech decisions

| Decision | Value |
|---|---|
| Language | Python 3.11+, single `archshift/` package |
| LLM | `claude-opus-5` via `anthropic` SDK, adaptive thinking, structured outputs |
| Isolation | Docker for build + correctness + benchmark; `--cap-add=PERFMON --security-opt seccomp=unconfined` when profiling |
| Per-run isolation | Fresh container + fresh temp dir per run, destroyed after |
| x86 host | Shared server, SSH + sudo. Noise control: `taskset` pin, `nice`, loadavg gate, CV discard |
| Arm64 host | School server (pending A2) — Graviton fallback available |
| Issue tracker | GitHub issues on `atshalahmedkhan/KAP_System`, wayfinder map + tickets |

---

Status against this plan is tracked in [status.md](status.md). Open decisions
live as wayfinder tickets on the issue tracker.
