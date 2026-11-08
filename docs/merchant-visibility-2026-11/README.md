# DigiKitPro — Google Merchant Center Visibility & Organic Growth Strategy (November 2026)

**Date:** 2026-11-08 · **Branch:** `arena/bc47b05e-digikitpro` · **Status:** strategy for review — **no live changes made** (per execution rules). PR #82 (bundle proposal) remains open separately.

## Correction to the brief's premise

The catalog submitted to Google Merchant Center is now **44 items, not 45**: `pro-sketch-traditional-art-kit` was held out of the feed on 2026-11-08 under your instruction (deliverable is a `.rar`; cover/contents unverified) — see `docs/merchant-audit-2026-11/00-HIGH-status.md` and PR #81. All counts in this pack say 44 live + 1 held. Also, two claims in the brief need honest qualification up front: we have **no Merchant Center or Search Console access in this environment**, so approval/impressions/CTR/indexing are **not inspectable from here**; and approval never guaranteed impressions — we plan for that explicitly.

## Evidence labels (as in the 2026-11 pack)

- **[Verified-public]** — on-page public counters seen 2026-11-08 (Creative Market sales, Etsy shop stats, review counts).
- **[Vendor-estimate]** — RankHero / Keywords Everywhere monthly averages, rounded; directional only (Google Trends returned 429 in Oct-2026 research).
- **[Repo]** — `google-merchant-feed.xml`, `data/products.json` (51 products), QA suites (115 verify / 1234 editorial / 18 merchant / 3207 SEO checks — all PASS as of this build).
- **[Official]** — Google help pages fetched 2026-11-08 (cited inline).
- **[Unknown]** — not measurable from here; never treated as zero.

## Deliverables

| # | File | Phase | Contents |
|---|---|---|---|
| 1 | `01-visibility-audit.md` | 1 | Feed audit, eligibility vs Free Listings requirements, where products can/cannot appear, owner-export checklist to find zero-impression items |
| 2 | `02-keyword-opportunities.md` | 2 | ~28 search opportunities mapped to products (evidence-labeled) |
| 3 | `03-optimization-44-products.csv` | 3 | All 44 feed items + the held SKU: before/after titles, identifiers, categories, flags, priorities |
| 4 | `04-landing-page-plan.md` | 4 | PDP audit vs feed requirements (parity rule) + conversion gaps |
| 5 | `05-organic-seo-strategy.md` | 5 | Internal-link/ladder strategy, cannibalisation guard, free→paid funnel, GSC playbook |
| 6 | `06-competitor-benchmarks.md` | 6 | 10 competitors through a Merchant-Center lens; what they beat us on vs what we beat them on |
| 7 | `07-90-day-traffic-plan.md` | 7 | Days 1–15 / 16–30 / 31–60 / 61–90 with priority, impact, difficulty, KPIs |
| 8 | `08-measurement-dashboard.md` | 8 | KPI table, weekly/monthly templates, segmentation rules, alert thresholds |

## The three things that decide whether any of this works (in order)

1. **Does the feed stay eligible?** US shipping settings and return policy in MC are mandatory for free listings in the US [Official] — currently unverified (audit register item E). If this is wrong, nothing else matters.
2. **Is anyone clicking?** Approval → impressions requires query-match + competitive titles/CTR. We rewrote titles 2026-10-29; the only CTR evidence is yours to pull (MC export).
3. **Does the site convert?** 51 PDP pages with structured data, honest before/after, free→paid ladder — solid foundations; reviews/social proof remain thin.

## Hard limits, restated

No credentials here → every "approved"/"impressions"/"indexed" statement in this pack is **structural** (repo + public web), not account data. Do not treat this document as proof of eligibility or of zero impressions. The owner-export step in `01-visibility-audit.md` closes that gap in under an hour.
