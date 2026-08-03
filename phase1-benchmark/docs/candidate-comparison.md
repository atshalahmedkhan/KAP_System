# Candidate comparison

## Initial repositories considered (then narrowed)

| Project | Category | Why not shortlisted / note |
|---|---|---|
| zlib-ng | Compression | Strong SIMD; deferred to keep shortlist at three |
| brotli | Compression | Heavier; overlapping with zstd |
| xz/liblzma | Compression | Build/test heavier for student scope |
| libpng | Image | Solid but less SIMD migration drama than libjpeg-turbo |
| qoi | Image | Smaller surface / less mature bench story |

## Final three candidates

1. **zstd** — [candidates/candidate-1.md](../candidates/candidate-1.md)
2. **LZ4** — [candidates/candidate-2.md](../candidates/candidate-2.md)
3. **libjpeg-turbo** — [candidates/candidate-3.md](../candidates/candidate-3.md)

## Weighted scores

| Criterion | Weight | Candidate 1 (zstd) | Candidate 2 (LZ4) | Candidate 3 (libjpeg-turbo) |
|---|---:|---:|---:|---:|
| Primarily C | 10% | 5 | 5 | 5 |
| Build simplicity | 10% | 5 | 5 | 4 |
| Test reliability | 15% | 5 | 5 | 5 |
| Benchmark reliability | 15% | 5 | 3 | 2 |
| Deterministic output | 15% | 5 | 5 | 4 |
| AMD64 compatibility | 5% | 5 | 5 | 5 |
| ARM64 compatibility | 10% | 4 | 3 | 3 |
| Docker reproducibility | 10% | 5 | 5 | 4 |
| Optimization potential | 10% | 5 | 3 | 5 |
| **Total (0–100)** | 100% | **97.0** | **84.0** | **81.0** |

## Evidence summary

- **zstd:** `make check` ×3 exit 0; five amd64 benches mean ~20.46 s CV ~2.7%; bit-identical `.zst` + round-trip; Make build; dual BSD/GPLv2 documented accurately.
- **LZ4:** `make test` ×3 exit 0; five amd64 benches mean ~11.13 s but CV ~16.5%; bit-identical frame + round-trip; Arm64 image built; full QEMU test suite interrupted.
- **libjpeg-turbo:** `ctest` 664/664 ×3; same-arch deterministic JPEG/oracle PPM; CV ~25%; lossy (no original-pixel equality); strongest SIMD story but cross-arch identity unproven; full QEMU suite not completed.

## Why not select the other two

- **LZ4:** Excellent simplicity and determinism, but weaker SIMD/architecture-specific surface for x86↔Arm research, higher timing CV, and dual BSD+GPL CLI licensing complexity. Lower weighted score.
- **libjpeg-turbo:** Best SIMD migration narrative, but lossy output complicates Phase 1 correctness, high timing variance, and cross-arch bit-identity not established. Hard veto risk if Arm NEON vs SSE diverge.

## Unresolved risks

- Full Arm64 automated test suites under QEMU were not completed for all candidates (time). Final selected app receives Arm64 image build + functional test/benchmark verification.
- zstd evaluation mean ~20 s with 20 iterations; packaged workload uses 10 iterations targeting ~10 s.

## Selection

**Selected: zstd (Candidate 1)** — highest score, no hard veto, deterministic round-trip, excellent CV, clear Make + Docker path, realistic optimization/SIMD follow-on work.
