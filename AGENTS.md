# AGENTS.md

Entry point for Codex and other agentic coding tools working in this repo.
Claude Code should instead read [CLAUDE.md](CLAUDE.md) (same content,
Claude-specific conventions) — both files link to each other and to
`docs/` so the two stay in sync.

## What this project is

**KAP System / ArchShift** — an autonomous pipeline that migrates x86
applications to Arm64, validates correctness, profiles performance, and
generates verified optimizations, built for the **Arm Create: AI
Optimization Challenge** hackathon (Cloud AI track).

Read in this order before doing any non-trivial work:

1. [docs/project-spec.md](docs/project-spec.md) — full spec: problem,
   scope, architecture, phases, safety rules, MVP definition
2. [docs/status.md](docs/status.md) — what's actually built vs. still spec
3. [docs/architecture.md](docs/architecture.md) — condensed component diagram
4. [docs/hackathon.md](docs/hackathon.md) — submission requirements, judging
   criteria, deadlines

## Ground rules for agents working here

- **Follow the build order in project-spec.md §16.** Don't jump ahead —
  e.g. no migration-agent code before a manual migration is documented
  (Phase 4 must precede Phase 6).
- **Never accept an unverified change.** Every patch must run on a temp
  branch, pass tests, and clear the benchmark noise threshold before it's
  treated as done. See project-spec.md §12 (safety rules) and §13 (scoring).
- **Preserve three states in any benchmark work:** original x86, migrated
  unoptimized Arm64, optimized Arm64. Don't overwrite or conflate results
  across these.
- **Keep docs/status.md current.** When you complete a phase or checklist
  item, update it in the same change — don't let the doc drift from the code.
- **Scope discipline.** One app, one repo, one container, one Arm target,
  one optimization attempt at a time (project-spec.md §5, §15). Resist
  scope creep even when it looks like an easy win.
- **Don't touch the phase1-benchmark artifacts casually.** `phase1-benchmark/`
  is a pinned, verified deliverable (zstd v1.5.7 @
  `f8745da6ff1ad1e7bab384bd1f9d742439278e99`, fixed input, expected output
  hashes). Changing it invalidates prior verification — if it must change,
  re-run and re-document verification per
  [phase1-benchmark/docs/phase1-verification.md](phase1-benchmark/docs/phase1-verification.md).

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
