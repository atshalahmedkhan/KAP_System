# Optimization Agent

`archshift.optimization.propose_optimization()` consumes a B1 profile JSON,
hotspot context, and build context, calls `claude-opus-5` with structured
outputs, and enforces the locked flag allowlist before returning a proposal.
