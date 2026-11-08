# Phase 8 — Measurement Dashboard & Reporting Templates (2026-11-08)

## 0. Ground rules

1. **Baseline before change** — fill §1 from exports before Day-1 actions land; every KPI below is a delta from that baseline.
2. **Free Listings ≠ Organic Google** — separate rows, separate filters; Google's own reports allow this (MC reports vs GSC). Never sum them into one "Google traffic" vanity number.
3. **Zero ≠ unknown** — export gaps are leaves blank with `OWNER`, never `0`.
4. 28-day windows by default; 7-day only for diagnostics.
5. No targets invented as guarantees — targets below are **reference bands** to review monthly; adjust after Month 1 real data.

## 1. Baseline snapshot (fill from exports before changes)

| Block | Metric | Baseline (2026-11-08: all OWNER) | Source |
|---|---|---|---|
| Feed | Items eligible / approved | OWNER (expect 44) | MC Products → All products |
| Feed | Disapprovals / warnings | OWNER | MC → Needs attention |
| MC | Impressions / clicks / CTR (28d) | OWNER | MC performance |
| MC | Impressions, clicks per product (export CSV; keep 44-row table) | OWNER | MC → All products → download |
| MC | Free listings destinationsplit (Search/Images/Shopping tab/YouTube/other) | OWNER | MC performance (if shown) |
| GSC | Clicks / impressions / CTR / avg position (28d + 16mo) | OWNER | GSC Performance |
| GSC | Indexed pages (of 101) / coverage errors | OWNER | GSC Coverage |
| GSC | Top 20 queries; striking-distance (pos 5–20) list | OWNER | GSC export |
| Site | Organic sessions → PDP; conversion assist | OWNER | Plausible/GA4 + Payhip |
| Store | Orders / revenue / refunds (90d) | OWNER | Payhip dashboard |
| Funnel | Freebie downloads; email signups; list size | OWNER | Payhip + ESP |
| Social | Pinterest impressions, outbound clicks | OWNER | Pinterest analytics |

## 2. Monthly KPI table (competition-ready)

| # | KPI | Definition / formula | Source | Window | Reference band (not guarantee) |
|---|---|---|---|---|---|
| 1 | MC impressions | SUM(impressions) all products | MC | 28d | +15–30% by Day 60 (post-eligibility only) |
| 2 | MC clicks & CTR | clicks = SUM(clicks); CTR = clicks/impressions | MC | 28d | CTR band 0.3–1.5% for shopping contexts (adjust vs own baseline) |
| 3 | Free-listings orders share | orders attributed to free listings ÷ total orders | Payhip+UTM (tag PDPs `utm_source=google&utm_medium=merchant_center` if possible) | 28d | growth month-over-month |
| 4 | Organic clicks (GSC) | SUM(clicks) | GSC | 28d | +20–40% by Day 90 w/ content live |
| 5 | Organic CTR | GSC clicks/impressions (site-wide; also per top-10 pages) | GSC | 28d | stable-or-up; investigate page-level drops >25% |
| 6 | Avg. position trend | GSC avg position | GSC | 28d | improving (lower = better) |
| 7 | Indexed pages | Coverage → Valid pages (of 101) | GSC | monthly | ≥95%; zero "excluded by noindex" surprises |
| 8 | Organic sessions to PDPs | sessions on /products/* | analytics | 28d | +25% by Day 90 |
| 9 | Product-page CVR | Payhip orders ÷ PDP sessions (or Payhip's own conversion stat) | Payhip + analytics | 28d | ≥ baseline; top flagship PDPs watched individually |
| 10 | Downloads (freebies) | count | Payhip | 28d | freebie funnel health |
| 11 | Email list growth | new subscribers ÷ list size | ESP | 28d | ≥3%/mo |
| 12 | Orders / revenue | SUM(order totals); net of refunds | Payhip | 28d | track; not a guarantee band — decision input |
| 13 | Bundle attach rate | bundle orders ÷ (bundle + component kits orders) | Payhip | monthly | ≥15% once System bundle live |
| 14 | Review count added | Δ reviews on site | manual | monthly | +5 founding per month |
| 15 | Feed health | approved items / 44; fetch errors | MC | monthly | 44/44 approved (or justified exclusions) |

## 3. Segmentation rules (learned-from-experience section)

- **Segment MC by custom_label_2 (price band) and custom_label_3 (priority cluster)** — our feed ships these precisely so you can see which class (brushes vs planners vs bundles) moves; export and pivot once monthly.
- **Separate "explained" from "unexplained" drops**: feed re-fetch → MC Diagnostics first, then GSC coverage, then site; never start with content.
- Seasonality: Nov–Dec = Christmas brushes tailwind; Jan–Feb = planner/fitness journals — read planners carefully against seasonal baseline, do not panic-fix.
- pro-sketch arrival: any prior-period pre-hold stats include it; note the break in the trendline annotation.

## 4. Weekly template (30 min)

```
DIGIKITPRO — Weekly visibility pulse — week of YYYY-MM-DD
Feed: approved items ×/44 · new warnings/disapprovals: ______ · fetch status: ______
MC (7d): impressions ____ · clicks ____ · CTR ____% · (vs 4-wk avg: __/__/__%)
MC top 3 products / bottom 3 zero-impression: ______________________________
GSC (7d): clicks ____ · impressions ____ · CTR ____ · coverage errors ____ (new: yes/no)
Site: organic sessions ____ → PDP ______ · freebie downloads ____ · email signups ____
Payhip: orders ____ · revenue $____ · refunds ____ · bundle orders ____
Alerts triggered (see §6): ________________________
One experiment in flight: ________________________
Escalate to owner if: ______________
```

## 5. Monthly template (owner review)

```
DIGIKITPRO — Monthly dashboard — YYYY-MM
1. Baseline reference (locked): ____________________
2. KPI table §2 with this month vs baseline & vs last month (Δ, %) — all 15 rows
3. MC vs Organic split summary (never merged)
   - MC: 44 approved? __ · impressions __ · CTR __ · top SKU ______ · bottom SKU (0-imp) ______
   - Organic: clicks __ · pos __ · striking-distance list (pos 5–20): ______________________
4. Content shipped this month & its early deltas (7-day impressions for new URLs)
5. Funnel: freebie → email → paid, by rung (free → Essential Line Art → Skin → Bundle → System)
6. Competitor watch: Gabrielle/Celine price moves, Kimmyw bundle, any new listicle placements, our review count vs theirs
7. What we learned (3 bullets) · what we'll test next month (3 bullets) · explicit kill list
8. Decisions needed from owner (e.g., feed exclusions for permanent-zero SKUs; H pro-sketch re-enable)
```

## 6. Alert thresholds (investigate when crossed)

| Signal | Trigger |
|---|---|
| Disapprovals | any new item disapproved >48h |
| Organic clicks | −30% wow with impressions stable (CTR collapse → title/SERP issue) |
| Impressions | −50% wow (possible indexing/feed issue → check MC + GSC immediately) |
| Coverage errors | any new "submitted but not indexed" affecting >3 URLs |
| Price/availability | ANY mismatch flag (rebuild feed immediately) |
| Refunds | >1/10 orders on a single SKU (quality check) |
| Bundle conversion | <5% of component-kit buyers clicking through (offer rework) |

## 7. Where the numbers live

`docs/growth-strategy-2026-11/baseline-2026-11.md` (CMC/GSC/Payhip/Pinterest intake tables) + this file's §5 monthly log — keep monthly logs appended in the doc or in `/docs/growth-strategy-2026-11/monthly/` if the owner prefers a file per month. Commit aggregates only; never commit customer data.
