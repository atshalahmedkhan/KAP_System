# CLAUDE.md

Guidance for Claude Code working in this repo. Codex and other agentic
tools should instead read [AGENTS.md](AGENTS.md) (same content, generic
conventions) — both files link to each other and to `docs/` so the two stay
in sync. If you edit one, mirror the change in the other.

## What this project is

**KAP System / ArchShift** — an autonomous pipeline that migrates x86
applications to Arm64, validates correctness, profiles performance, and
generates verified optimizations, built for the **Arm Create: AI
Optimization Challenge** hackathon (Cloud AI track).

Read in this order before doing any non-trivial work:

1. [docs/revised-plan.md](docs/revised-plan.md) — **the operative plan.**
   Nine-day scope, schedule, the three components being built, correctness
   definition, risks. Supersedes project-spec.md §9/§16.
2. [docs/status.md](docs/status.md) — what's actually built vs. still planned
3. [docs/hackathon.md](docs/hackathon.md) — verified deadline, eligibility,
   judging criteria
4. [docs/project-spec.md](docs/project-spec.md) — long-term product spec.
   Still the reference for architecture, safety rules, and MVP definition;
   **its 21-phase plan and build order are superseded.**
5. [docs/architecture.md](docs/architecture.md) — component diagram

## Ground rules for agents working here

- **The deadline is 2026-08-14 16:00 PT.** Scope is
  [revised-plan.md](docs/revised-plan.md) §3 — three components built deep
  (Profiling Engine, Optimization Agent, Verification & Safety Engine),
  everything else specced into `docs/deferred/`. Do not start building a
  deferred component without an explicit decision to change scope.
- **Never accept an unverified change.** Every patch must run on a temp
  branch, pass tests, and clear the benchmark noise threshold before it's
  treated as done. See project-spec.md §12 (safety rules) and §13 (scoring).
- **Preserve three states in any benchmark work:** original x86, migrated
  unoptimized Arm64, optimized Arm64. Don't overwrite or conflate results
  across these.
- **Respect the tiered correctness definition** in revised-plan.md §4.
  Arm-to-Arm comparisons require an exact output-hash match; x86-to-Arm
  comparisons do not, because cross-architecture float divergence is expected.
  Don't write a checker that demands bit-exactness across architectures.
- **Rejections are deliverables.** A logged, explained rollback is headline
  evidence — never suppress or discard one to make a run look clean.
- **Keep docs/status.md current.** When you complete a task, tick it in the
  same change — don't let the doc drift from the code.
- **The benchmark app is llama.cpp**, not zstd. The old `phase1-benchmark/`
  (zstd) was removed in the 2026-08-05 replan; it lives in git history at
  commit `a44631a` if its harness scripts are wanted.

## Skills to reach for

Vendored in-repo at `.claude/skills/<name>/` (Claude Code) and
`.agents/skills/<name>/` (Codex) — real files, checked into git, not a
global-plugin dependency. Update via `npx skills@latest update`, tracked in
[skills-lock.json](skills-lock.json).

- **`wayfinder`** — chart large, foggy chunks of work (e.g. Phase 6
  migration agent, Phase 11 optimization agent) as decision tickets before
  building. Reach for it instead of diving straight into code when a phase
  is bigger than one session. Invoke with `/wayfinder`.
- **`grilling` / `grill-me`** — stress-test a plan or design before
  committing to it. Use before starting a new phase, or when proposing a
  non-obvious architecture decision (e.g. scanner rule design, scoring
  weights).
- **`git-guardrails-claude-code`** (setup-only) — installs a PreToolUse hook
  blocking `git push`, `reset --hard`, `clean -f`, `branch -D`. Worth
  running once given how much of this project is autonomous agent-driven
  git operations.

## Repo layout

See [docs/status.md](docs/status.md#repo-layout) for the current tree.

---

Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.
