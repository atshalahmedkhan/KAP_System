# Deferred components

Design docs for ArchShift components that are **specified but not built** in
the 9-day hackathon window. See [revised-plan.md](../revised-plan.md) §3 for
why: two people, ~75 person-hours, so three components are built deep and the
rest are documented well enough to be picked up later.

These are submission assets in their own right — they show the full system was
designed, not just the slice that shipped — and they are the pickup queue if
spare hours appear.

## Pickup order

1. **Repository Scanner** — rule-based detection of x86-specific issues
   (Dockerfiles, CI configs, build scripts, base images, native deps, asm).
   Rules should be derived from the manual migration documented in task C2, not
   invented up front.
2. **Migration Agent** — plan-then-patch over the scanner's output, with
   confidence and risk levels per proposed change.
3. **Build Runner** — clone, isolated branch, `docker buildx build --platform
   linux/arm64`, log capture, retry limit.
4. **GitHub PR automation** — branch, commits, PR with the full evidence bundle
   attached.
5. **Web dashboard** — the six-screen UI from project-spec.md §7.1/§9 Phase 15.
   Superseded for this submission by the generated static HTML report (D2).

## What each doc needs

Enough that someone can start building without re-deriving the design:

- The component's inputs and outputs, as concrete schemas
- Where it sits in the pipeline, and what it assumes about its neighbours
- The two or three design decisions that were made, and what was rejected
- Known unknowns — what still needs a decision before implementation

Reference: [project-spec.md](../project-spec.md) §7 for each component's
original responsibility, and [architecture.md](../architecture.md) for how
they connect.
