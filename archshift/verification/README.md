# Verification & Safety Engine

`VerificationEngine` evaluates at most three B2 proposals in isolated Git
worktrees. For each attempt it enforces build → Arm-to-Arm output-hash
correctness → benchmark. Measurements use two discarded warm-ups and seven
timed iterations; a state with CV above 10% is re-run before comparison.

Acceptance requires a strictly positive improvement greater than both the
variance floor (`3 × baseline stdev`) and five percent of baseline mean.
Every rejection resets and removes its worktree, retains its branch ref, and
appends the issue #6 evidence record to the configured JSONL log. Patches that
modify tests, benchmarks, or verification code are rejected before build.
