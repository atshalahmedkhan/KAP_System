# Project status

Tracks actual repo state against [project-spec.md](project-spec.md) §9/§16.
Update this file whenever a phase completes — don't let it drift from the
code, it's the fastest way for an agent (or a human) to know what's real vs.
planned.

## Current phase: Phase 1 complete → starting Phase 2

### Phase 0 — Project definition: ✅ complete
One-page spec, target user, scope, success criteria all defined. See
[project-spec.md](project-spec.md).

### Phase 1 — Select benchmark application: ✅ complete
- **Selected:** zstd v1.5.7, commit `f8745da6ff1ad1e7bab384bd1f9d742439278e99`
- Evaluated against LZ4 and libjpeg-turbo (both rejected — see
  [phase1-benchmark/docs/candidate-comparison.md](../phase1-benchmark/docs/candidate-comparison.md))
- Working Dockerfile, fixed 32 MiB input, expected output pinned with SHA-256
- amd64 verified natively; arm64 verified functionally under QEMU (not a
  performance measurement — native Arm hardware still needed)
- amd64 benchmark: mean 8.128295s, CV ~2.28%, correctness PASS
- Full writeup: [phase1-benchmark/README.md](../phase1-benchmark/README.md),
  [phase1-benchmark/docs/phase1-verification.md](../phase1-benchmark/docs/phase1-verification.md),
  [phase1-benchmark/docs/reproducibility.md](../phase1-benchmark/docs/reproducibility.md)

**Two Phase 1 checklist items remain open in the spec but are effectively
covered by the artifacts above** — worth double-checking before moving on:
fixed benchmark input (done: `benchmark/inputs/input.bin`) and expected
output storage (done: `benchmark/expected/`).

### Phase 2 — Prepare infrastructure: not started
Need: real x86 machine/instance spec record, real AWS Graviton (or
equivalent) Arm64 instance with SSH, isolated per-run workspaces, timeouts,
storage/CPU/memory limits, failed-run logging. Everything done so far for
Arm64 has been QEMU emulation — this phase is where native Arm hardware
enters the project for the first time.

### Phase 3 onward — not started
See [project-spec.md](project-spec.md) §9 for the full phase list and §16
for the exact build order. Do not skip ahead — Phase 4 (manual migration)
must happen before any migration agent code is written, per spec §14/§16
rule 4-12-13.

## Repo layout

```
KAP_System/
├── AGENTS.md                  # agent entry point (Codex / general)
├── CLAUDE.md                  # agent entry point (Claude Code)
├── README.md                  # top-level project README
├── docs/                      # this folder — hackathon + spec + status
│   ├── hackathon.md
│   ├── project-spec.md
│   ├── architecture.md
│   └── status.md
└── phase1-benchmark/           # Phase 1 deliverable (zstd benchmark package)
    ├── Dockerfile
    ├── benchmark/               # inputs, expected outputs, results
    ├── candidates/               # candidate-1/2/3 evaluation notes
    ├── container/                 # build/test/benchmark/verify shell scripts
    ├── docs/                       # phase1-specific docs (selection, verification, reproducibility)
    └── scripts/                     # PowerShell build/test/benchmark scripts (Windows host)
```
