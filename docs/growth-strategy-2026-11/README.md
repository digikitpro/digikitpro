# DigiKitPro — Advanced SEO, Competitor Intelligence & Market Growth Strategy (November 2026)

**Date:** 2026-11-08 · **Scope:** whole store, ~45 Merchant Center items, repo `digikitpro` on `arena/c5d5128e-digikitpro`
**Author context:** strategy session for the store owner; all findings must be evidence-labelled. Nothing here is a ranking or revenue guarantee.

## How to read the evidence labels

- **[Verified-public]** — on-page public counters (e.g. Creative Market "1,106 sales", Etsy shop headers "8.8k sales · 1.1k reviews", star-ratings, favourites counts, timestamps) captured 2026-11-08. These are the platforms' own published numbers, not third-party audits.
- **[Vendor-estimate]** — RankHero / Keywords Everywhere monthly averages (see `docs/KEYWORD-RESEARCH-2026-10-29.md`). Directional, rounded, months differ; **not first-party October counts**.
- **[Repo]** — derived from this repository: `google-merchant-feed.xml`, `data/products.json` (51 products), QA suites (115 site checks, 3207 SEO checks, 1239 editorial checks, all passing 2026-11-08).
- **[Unknown]** — not measurable from this environment; never treated as zero.

## Hard limitations (read first)

1. **No Keyword Planner / Trends access.** Google Trends returned HTTP 429 in the October research; no Trends readings were recovered. Volume figures below are [Vendor-estimate] only.
2. **No Google Search Console or Merchant Center API access** from this sandbox. Indexing state, canonical selection, category 500046 validity and impressions/CTR must be confirmed by the owner in the GSC/MC UIs.
3. **Payhip is not reachable from this environment.** The two confirmed counts (43 brushes + 1 bonus; 252+ assets) come from the owner-confirmed Payhip listings and the scraped catalog — not a live re-check today.
4. **Competitor sales are not audited books.** [Verified-public] counters are platform-displayed figures; treat as strong signals, not audited revenue.
5. This is a strategy, not executed change. P0 fixes are flagged; nothing in the live feed/site was modified by this document.

## Deliverables

| # | File | Phase | Contents |
|---|---|---|---|
| 1 | `01-market-research.md` | 1 | What customers want right now; 9 research questions answered |
| 2 | `02-competitor-intelligence.md` | 2 | 10 competitors, evidence of commerce, weaknesses |
| 3 | `03-keyword-architecture.csv` | 6 | Keyword → target page map (~70 rows) |
| 4 | `04-seo-audit.md` | 4 | Technical + on-page audit, findings by priority |
| 5 | `05-merchant-center-45-products.csv` | 5 | 45-product feed review vs current values |
| 6 | `06-market-gap-report.md` | 3 | 18 market opportunities (improve-or-build) |
| 7 | `07-product-development-roadmap.md` | 8 | 6 proposed products with pricing evidence |
| 8 | `08-content-strategy-90-day.md` | 7 | 12 article briefs + publishing plan |
| 9 | `09-pinterest-and-channels.md` | 9 | Pinterest strategy + other discovery channels |
| 10 | `10-growth-roadmap-90-day.md` | 10, 11 | Prioritised 90-day plan + measurement & baseline |

## Headline conclusions

1. **The niche is real and rankable.** "procreate portrait brushes" is small (RankHero ~70 global avg) but brutally competitive; the winning play is long-tail + problem keywords ("why do my digital portraits look plastic") with genuinely demonstrated expertise — exactly where DigiKitPro already has assets (before/after slider, workflow-organised kits).
2. **The single biggest free win is feed hygiene.** A product ships to Google with internal-audit caveats in its highlights today (see #4 P0-1); fixing that costs minutes.
3. **Price ladder gap**: DigiKitPro $5–8 competes on value against Etsy budget sets ($4.80) and Creative Market mid-tier ($18–50). There is room for one $19–29 "complete system" bundle to anchor perceived value, following the Lisa Glanz tutorial-included model.
4. **Reputation signals are thin off-site.** No reviews widget, no Trustpilot, marketplace presence absent — competitors monetise Etsy/Creative Market trust. A deliberate Pinterest + freebie→email funnel is the lowest-cost authority builder available.
5. **Do the boring things first**: feed fixes, count confirmations, baseline capture (GSC/MC) — then content velocity. Velocity before foundations wastes every article.
