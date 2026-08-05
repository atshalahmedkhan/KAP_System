# Agent routing — which model works which task

This repo expects work to be picked up by AI coding agents, often unattended.
Each task issue is tagged with a **model tier**. Match the agent to the tier —
using an expensive model on a mechanical task wastes budget; using a cheap
model on a design-heavy task produces work that needs redoing.

## Tiers

| Tag | Claude | Codex | Use for |
|---|---|---|---|
| `model:simple` | Haiku 4.5 | Codex 5.6 Luna | Scaffolding, config, mechanical wiring, running documented recon steps, glue code between already-defined pieces. Low ambiguity — the task issue fully specifies the shape of the output. |
| `model:complex` | Sonnet 5 | Codex 5.6 Tera | Schema design, correctness-critical logic (verification gates, accept/reject rules), prompt engineering against the Anthropic API, anything where the task issue states a goal but the implementation has real design decisions inside it. |

If a task is a toss-up, prefer the complex tier — a wrong mechanical shortcut
in the Verification & Safety Engine is exactly the kind of bug this project's
safety rules exist to catch (project-spec.md §12).

## Picking up a task

1. Read the linked GitHub issue in full — acceptance criteria, dependencies,
   the stub PR it's paired with.
2. Check the issue's `blocked-by` list (rendered natively by GitHub). If it's
   not empty and those issues aren't closed, don't start — the design
   decision you need hasn't been made yet. Work a decision ticket
   (`wayfinder:*` label) instead, or pick a different unblocked task.
3. Claim the issue: assign yourself, first, before writing any code.
4. Check out the paired stub branch (named in the issue). It has a draft PR
   already open — push commits to that branch, the PR updates automatically.
5. Before marking the PR ready for review: run tests, confirm it matches the
   acceptance criteria in the issue, update `docs/status.md` in the same PR.
6. Mark the PR ready for review (undraft it). Don't merge it yourself unless
   explicitly told to — these are reviewed by Kritarth or the teammate before
   landing, per the project's safety rules on unverified changes.

## Context every agent needs before starting

Read in this order — same order as [CLAUDE.md](../CLAUDE.md) /
[AGENTS.md](../AGENTS.md):

1. [revised-plan.md](revised-plan.md) — the operative 9-day plan
2. [status.md](status.md) — what's built vs. planned
3. The specific task issue
4. Any wayfinder decision ticket (`wayfinder:*` label) it references — the
   decision ticket holds the design answer; the task issue holds the
   acceptance criteria

## What not to do

- Don't start a task whose `blocked-by` isn't closed. The decision hasn't
  been made — building ahead of it produces throwaway work.
- Don't touch `docs/deferred/` components. Out of scope for the 9-day window
  (revised-plan.md §3) unless explicitly reassigned.
- Don't merge your own PR.
- Don't skip the noise-control steps in benchmark tasks (`taskset` pin,
  `nice`, loadavg gate, CV discard) — a benchmark number without them is not
  evidence, per revised-plan.md §8.
