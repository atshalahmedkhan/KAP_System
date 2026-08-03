# ArchShift Project Specification

Full spec for KAP System / ArchShift: agentic x86-to-Arm migration and
optimization pipeline. This is the source of truth for scope, phases, and
safety rules. Agents (Claude, Codex) should read this before proposing
architecture changes. See [status.md](status.md) for what's actually built
vs. what's still spec.

## 1. Core project statement

An autonomous performance-engineering agent that migrates x86 applications
to Arm64, identifies architecture-specific performance bottlenecks,
generates safe code optimizations, and verifies every change through
automated testing and benchmarking.

## 2. Problem

Cloud applications built for x86 (Intel/AMD) can often run cheaper, cooler,
and sometimes faster on Arm infrastructure (e.g. AWS Graviton). Migration is
blocked by:

- Incompatible dependencies, x86-only Docker images
- Build config and CI updates
- Architecture-specific code, native module recompilation
- Correctness testing across architectures
- Profiling on real Arm hardware, cache/memory bottleneck analysis
- Applying Arm-specific optimizations

These require engineers who know cloud infra, computer architecture,
compilers, containers, and profiling — a rare combination. ArchShift
automates a large part of this.

## 3. Proposed solution

User connects a GitHub repo + test/benchmark commands. ArchShift:

1. Scans the repository
2. Detects x86-specific compatibility problems
3. Generates an Arm migration plan
4. Creates an Arm64-compatible version
5. Builds on Arm infrastructure
6. Runs automated tests
7. Compares outputs (x86 vs Arm)
8. Benchmarks the migrated app
9. Profiles performance bottlenecks
10. Generates one targeted optimization
11. Tests the optimized version
12. Benchmarks the optimized version
13. Rejects changes that break correctness or reduce performance
14. Opens a GitHub PR with verified changes + evidence

## 4. Target users

Platform engineering, DevOps, cloud infra teams, SaaS companies moving to
Graviton, enterprises with legacy x86 apps, OSS maintainers adding Arm64
support, cost-optimization engineers, systems researchers.

## 5. Initial scope (intentionally narrow)

**Supported (v1):**
- One C/C++ application, one repo, one Docker container
- One Arm64 target server, one benchmark workload, one optimization attempt at a time

**Application must have:** repeatable I/O, automated tests, a Dockerfile,
CPU/memory-intensive operations (loops, matrix ops, numerical work), a
benchmark long enough to measure reliably.

**Application must NOT have:** multiple microservices, GPU requirements,
distributed DBs, multiple languages, unstable outputs, missing tests, heavy
prod dependencies, complex auth.

**Selected benchmark app (Phase 1, complete):** zstd v1.5.7, commit
`f8745da6ff1ad1e7bab384bd1f9d742439278e99`. See
[phase1-benchmark/docs/benchmark-selection.md](../phase1-benchmark/docs/benchmark-selection.md).

## 6. Success criteria (MVP)

- Accept one GitHub repo
- Detect ≥1 x86-specific compatibility problem
- Generate Arm64-compatible Docker config
- Build successfully on an Arm server
- Pass all existing tests
- Verify x86/Arm output match
- Measure performance, identify ≥1 bottleneck
- Generate one targeted optimization
- Reject a correctness-breaking optimization
- Reject a performance-regressing optimization
- Preserve an optimization with measurable improvement
- Generate a PR with benchmark evidence

## 7. System architecture

| Component | Responsibility |
|---|---|
| 7.1 Web Dashboard | Connect repo, configure commands/target, view all results, open PR |
| 7.2 Repository Scanner | Detect x86-specific issues: Dockerfiles, CI, build scripts, deps, binaries, asm, base images |
| 7.3 Migration Agent | Read scan → plan → limited patches to Docker/deps/CI/build |
| 7.4 Build Runner | Clone, isolated branch, build x86 + Arm64, logs, image sizes |
| 7.5 Correctness Validator | Unit/integration/API tests, output diffing, crash/numerical-diff detection |
| 7.6 Benchmarking Engine | Exec time, throughput, CPU/mem, image size, build duration, variance, cost |
| 7.7 Profiling Engine | CPU hotspots, cache misses, branch/pipeline stalls, vectorization, instruction mix |
| 7.8 Optimization Agent | Read benchmark+profiling → one focused patch + expected impact |
| 7.9 Safety & Rollback Engine | Attempt limits, mandatory tests, auto-rollback on regression, rejection logging |
| 7.10 GitHub Integration | Branch, commits, PR with full evidence bundle |

## 8. End-to-end workflow

```
connect repo → clone → x86 baseline build+test → compatibility scan
  → migration plan → migration patch → Arm64 build → correctness tests
  → (retry on failure) → unoptimized Arm benchmark → profiling
  → optimization patch → correctness tests → benchmark again
  → accept or reject → verified results → pull request
```

## 9. Development phases

Full phase breakdown (0–21) with detailed task checklists lives in the
original spec history; the operative summary:

- **Phase 0** — Project definition ✅
- **Phase 1** — Select benchmark application ✅ (zstd, see [status.md](status.md))
- **Phase 2** — Prepare x86 + Arm64 infrastructure (isolation, timeouts, limits)
- **Phase 3** — x86 baseline metrics (5+ iterations, warm-up, raw + averaged)
- **Phase 4** — Manual migration first — **do not build the agent before one successful manual migration**
- **Phase 5** — Repository scanner (rule-based, from manual-migration learnings)
- **Phase 6** — Migration agent (plan-then-patch, confidence/risk levels)
- **Phase 7** — Automated Arm64 build (`docker buildx build --platform linux/arm64`, max 3 retries)
- **Phase 8** — Correctness validation (unit/integration/output-diff/runtime)
- **Phase 9** — Unoptimized Arm benchmark (preserve x86 / Arm-baseline / Arm-optimized as 3 distinct states)
- **Phase 10** — Performance profiling (hotspots, cache, memory, vectorization)
- **Phase 11** — Optimization agent (loop reorder, locality, vectorization, NEON, etc.)
- **Phase 12** — Self-healing loop (generate → apply → build → test → reject/rollback → benchmark → reject/rollback → preserve)
- **Phase 13** — Scoring system (correctness 50%, performance 25%, quality 10%, reliability 10%, resource 5%; ≥5% improvement threshold, tuned to variance)
- **Phase 14** — GitHub PR automation (full evidence bundle)
- **Phase 15** — Dashboard (6 screens: setup, compatibility, build/validation, profiling, optimization, final comparison)
- **Phase 16** — Expand to 3+ workload types
- **Phase 17** — Research evaluation (research questions, metrics, baselines)
- **Phase 18** — Production readiness (security, reliability, observability)
- **Phase 19** — Hackathon submission
- **Phase 20** — Professor/research outreach
- **Phase 21** — Startup/YC positioning

**Build order is sequential — do not skip ahead.** See §16 below.

## 10. Recommended stack

- **Frontend:** Next.js, TypeScript, Tailwind, shadcn/ui, Recharts
- **Backend:** FastAPI or Node.js, PostgreSQL, Redis (job queues), background workers, Docker
- **Infra:** AWS EC2 x86 + Graviton Arm64, Docker Buildx, GitHub Actions, Terraform (later)
- **Analysis:** Arm MCP Server, migrate-ease, skopeo, static analysis, compiler output analysis
- **Profiling:** Arm Performix, Linux perf, llvm-mca, flame graphs
- **Agent:** one coding-capable LLM, structured JSON outputs, tool-calling, patch-based editing, strict prompts, limited retries
- **Observability:** structured logs, OpenTelemetry, agent action history, benchmark history

## 11. Data models (summary)

`Project`, `ScanResult`, `BuildRun`, `TestRun`, `BenchmarkRun`,
`OptimizationAttempt` — field lists match the report structures in §7 above
(compatibility score/issues, build status/duration/size, tests
passed/failed/output-hash, execution-time/throughput/memory/variance,
hypothesis/patch/result/accepted-or-rejected).

## 12. Safety rules (mandatory, non-negotiable)

- Every change on a temporary branch; every patch stored and reviewable
- Tests run after every patch; benchmarks run after every *valid* patch
- Incorrect changes roll back; slower changes roll back
- Agent cannot: touch protected branches, access unrelated repos, expose
  secrets, run unrestricted shell commands, exceed the attempt limit
- Agent must explain the reason for every change

## 13. Key metrics

**Technical:** migration success rate, build success rate, test
preservation rate, avg/median performance improvement, memory/image-size
reduction, cache-hit improvement, optimization acceptance rate, regression
rejection rate, avg agent attempts.

**Product:** time saved per migration, repos analyzed, PRs generated, PR
acceptance rate, estimated infra savings, active/repeat users.

## 14. Risks & mitigations

| Risk | Response |
|---|---|
| Scope creep | One language, one app, limited optimization types, engine before dashboard |
| AI produces incorrect code | Patch limits, mandatory tests, output comparison, auto-rollback |
| Unreliable perf results | Multiple iterations, warm-up, variance tracking, stable machines, noise-threshold rejection |
| Arm tooling friction | Manual pass first, document commands, add tools incrementally, `perf` fallback |
| Looks like "an AI wrapper" | Show real profiling data, real migration, verified diffs, real benchmark deltas, rejected attempts |
| Unclear market | Interview infra engineers / Graviton users, measure cost/time, validate willingness to pay |

## 15. Explicitly out of scope initially

Every language, multi-cloud, full autonomous prod deploy, advanced billing,
team permissions, complex design systems, mobile, GPU optimization,
Kubernetes migration, multi-repo, agent marketplace, long-term memory
system. **Build the engine first.**

## 16. Exact build order

1. Select benchmark repo ✅
2. Build manually on x86
3. Record x86 baseline
4. Create Arm64 environment
5. Migrate manually
6. Run tests on Arm
7. Compare outputs
8. Record unoptimized Arm baseline
9. Profile manually
10. Apply one manual optimization
11. Verify it
12. Document the whole manual process
13. Turn findings into scanner rules
14. Automate repo cloning
15. Automate scanning
16. Add migration agent
17. Automate Arm64 build
18. Automate correctness validation
19. Automate benchmarking
20. Automate profiling
21. Add one optimization strategy
22. Add rollback
23. Add scoring system
24. Add PR creation
25. Build dashboard
26. Test two additional workloads
27. Research evaluation
28. Website
29. Demo recording
30. Submit

## 17. MVP definition

The MVP is complete **only** when the full chain works end to end:
repo connected → x86 issues detected → migration generated → Arm64 built →
tests pass → outputs match → Arm baseline measured → bottleneck identified
→ optimization generated → tests pass again → performance improved → PR
created.

A dashboard without this workflow is not an MVP. An agent that only
recommends changes (doesn't verify) is not an MVP. A migration without
correctness validation is not an MVP. An optimization without benchmark
evidence is not an MVP.

## 18. Final expected outcome

Prove that a profiling-guided agent can **safely** migrate and optimize a
limited set of workloads while producing measurable, reproducible evidence
— not that AI can optimize anything.
