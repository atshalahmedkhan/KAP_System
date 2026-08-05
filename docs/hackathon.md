# Hackathon: Arm Create — AI Optimization Challenge

Source: https://arm-ai-optimization-challenge.devpost.com/rules

> **Dates verified 2026-08-05** directly from the Devpost rules page. The
> earlier conflicting dates in this file have been corrected.

## Basics

- **Name:** Arm Create: AI Optimization Challenge
- **Prize pool:** $8,000
  - Overall winner: $3,000 + blog post
  - Runner-up: $2,000 + blog post
  - Best in each track (3 awards): $1,000 each + blog post
  - A project wins at most one grand prize and one blog feature

## Dates (verified)

| Milestone | When |
|---|---|
| Submission window opens | 2026-06-10 09:00 PT |
| **Submission deadline** | **2026-08-14 16:00 PT** |
| Judging | 2026-08-17 09:00 PT → 2026-09-04 16:00 PT |
| Winners announced | ~2026-09-15 14:00 PT |

## Tracks

1. **Physical AI** — robotics, embedded devices, sensors, edge systems
2. **Cloud AI** — scalable infrastructure, Arm64 cloud deployment
3. **Mobile AI** — on-device optimization for phones, tablets, laptops

**KAP System / ArchShift targets Track 2 — Cloud AI.**

## Judging criteria (100 pts)

| Criterion | Points |
|---|---|
| Technological Implementation | 40 |
| User Experience / Developer Experience | 15 |
| Potential Impact | 20 |
| "WOW" factor | 25 |

Implication for us: correctness+benchmark evidence and a working end-to-end
loop matter more than UI polish, but the dashboard (Phase 15) is what
delivers the DX/WOW points — don't skip it.

## Submission requirements

- Public GitHub repository, **MIT or Apache 2.0** license
- Project description: features + purpose
- Setup instructions for an Arm-powered device / Arm64 environment
- Optional demo video, under 3 minutes (YouTube/Vimeo/Youku)
- Track 1 & 2: complete source code required
- Track 3 only: proof artifacts (screenshots/links) suffice — not our track

## Eligibility

Open to individuals at the age of majority, teams, and organizations. Closed
to residents of countries where US law prohibits participation (Brazil,
Quebec, Russia, Crimea, Cuba, Iran, North Korea, OFAC-designated territories),
and to Arm employees/family, judges, and conflicted entities.

Submissions must be original work solely owned by the **entrant** (the
individual or team submitting). Projects developed under contract with Arm, or
that received prior financial or preferential support from Arm, are excluded.
Building on open-source software is fine as long as the entrant creates
software that enhances and builds upon it.

**The mandatory requirement: create, migrate, or optimize an *AI solution* on
Arm architecture.** This is why the benchmark app was switched from zstd to
llama.cpp — see [revised-plan.md](revised-plan.md) §1.

Projects must show **clear optimization work with measurable improvement** —
model size, quality, speed, inference performance, DX, or other Arm-specific
gains. That is the whole thesis of ArchShift: every accepted change carries
benchmark evidence.

## Infrastructure constraints

**None.** The rules contain no prohibition on specific cloud providers,
infrastructure vendors, paid services, or commercial tools. Renting Arm64
compute (AWS Graviton, Oracle Ampere, etc.) is permitted — relevant to the
fallback in [revised-plan.md](revised-plan.md) §8.

A free **Arm Developer Program** account is required for dashboard access and
developer tools.

## Action items before submission

- [x] Verify actual start/end dates on the Devpost page — done 2026-08-05
- [ ] Sign up for the free Arm Developer Program account
- [ ] Pick and add an MIT or Apache-2.0 `LICENSE` file at repo root
- [ ] Confirm repo stays public
- [ ] Write Arm64 setup instructions (explicitly required)
- [ ] Record demo video, under 3 min (optional but strongly recommended for WOW)
- [ ] Write submission description from [revised-plan.md](revised-plan.md) §2–4
