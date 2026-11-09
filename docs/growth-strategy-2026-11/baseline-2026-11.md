# Growth baseline — November 2026 (template + repo-derived metrics filled)

Owner-side gap flagged throughout: GSC/MC/Payhip/Pinterest exports landed 2026-11-08 (GSC) — §B is filled with real values; the rest remains `OWNER` until those land. Repo-derived figures (all re-verified 2026-11-08 on `arena/09bf8858-digikitpro` after the PR #81 feed hold):

## A. Store & feed (filled from repo)

| Metric | Value (2026-11-08) | Source |
|---|---|---|
| Catalog products | 51 | `data/products.json` |
| Feed items | **44** (was 45) | `google-merchant-feed.xml`; pro-sketch held via `FEED_HOLDS` |
| Free products (excluded from feed) | 4 free brushes/palettes/guide + masterclass ebook $19 + Morocco PDF $5 excluded by policy | feed builder log |
| Price ladder | $4 (Halloween PNG) — $19 (Masterclass / Master Library $19) | products.json |
| Feed eligibility rule | paid, non-book, not comingSoon, not FEED_HOLDS | build log |
| QA state | verify 115/115 · editorial 1234 · feed 18/18 · SEO 3207 checks / 104 pages · guide 7/7 | suites |
| Sitemap | 101 URLs · 173 images · 18 articles · 10 HowTo blocks | qa_seo |
| Highlights >4 / details >5 | 36 / 20→21 (recheck on next rebuild) | audit register |
| Confirmed counts (owner) | essential-line-art 43+1; ultimate-bundle 252+ | Payhip listings (2026-11-08) |
| Count verified this pass | mega 650+ · library 2,000+ · vault 1,000+ · palette 160+12 | `06-count-verification-2026-11-08.md` |
| Unconfirmed counts | male-pose · female-pose · koi-fish · professional-hair (listing-stated nowhere); wellness planner (files/dates + leaked checklist) | same |
| Held from feed | pro-sketch-traditional-art-kit (.rar) — PR #81 | FEED_HOLDS |
| Known buyer-visible caveats | 9 items (see register addendum / PR #81) — pending your decision | feed XML |
| Structural schema | Product + Breadcrumb + HowTo (10×) + article markup present; validated structurally only | qa_seo |

## B. Google Search Console — export received 2026-11-08 (Web search, last 3 months; analyzed in [../gsc-baseline-2026-11-08.md](../gsc-baseline-2026-11-08.md))

Sources: owner exports `Chart.csv`, `Pages.csv`, `Queries.csv`, `Countries.csv`, `Devices.csv`, `Chart-2.csv` (Indexing, dated 2026-10-23), `Critical issues.csv` — Web type, "Last 3 months", range 2026-09-12 → 2026-11-06. Note: the index counts are from the Indexing export (to 2026-10-23); treat with a 2-week lag. Pages export sums to 299 vs Chart/Countries 294 — export rounding; use 294.

| Metric | Value |
|---|---|
| Total impressions / clicks / CTR / avg position | **294 / 0 / 0.00% / ≈10.0** (impr-weighted) |
| Indexed vs submitted (101 URLs) | **6 of ~12 known/processed** (Indexing report, 2026-10-23); fell from 9 between Sep 15–22 |
| Top queries (all tiny) | *procreate brushes difference* 2 imp @10 · *best lineart brush procreate* 2 @42 · *procreate skin brush* 1 @29 · *procreate portrait brushes* 1 @51 · *procreate line brush(es)* 1 each @62–71 |
| Impression-earning pages (all blog; clicks 0) | how-to-choose-procreate-brushes 109 @8.59 · best-procreate-brushes-for-anime 78 @8.41 · realistic-skin-in-procreate 31 @8.0 · make-digital-art-look-traditional 27 @10.33 · best-line-art 16 @28 · best-portraits 15 @12.33 · blending-brushes 13 @10.31 · realistic-hair 10 @7.6 (top-4 carry ≈83%) |
| Striking distance (pos 5–20) | how-to-choose 8.59, anime 8.41, realistic-skin 8.0, make-traditional 10.33, best-portraits 12.33, blending 10.31, realistic-hair 7.6 — all 0 clicks (CTR problem / rich-result eligibility) |
| Coverage issues ("Crawled – currently not indexed") | **1 page** (identity unknown — needs URL Inspection); plus "Alternate page with proper canonical tag" ×3 and "Page with redirect" ×2, all Validation: Started |
| Country split | US 113 (38%) · UK 30 · CA 14 · AU 12 · IN 10 · TH 8 — 53 countries total |

Export path: GSC → Performance → Search results → Export (CSV); Indexing → Pages → Export.

**Action gating:** coverage knowledge here precedes the first impressions/clicks growth — see [../owner-kits/first-clicks-2026-11.md](../owner-kits/first-clicks-2026-11.md) §A–B. No title/content churn accepted from this data.

## C. Merchant Center — OWNER export (90 days)

| Metric | Value |
|---|---|
| Total impressions / clicks / CTR | OWNER |
| Clicks & impressions **per product** (top/bottom 5) | OWNER |
| Disapprovals / warnings (esp. `500046` category flag) | OWNER |
| Click-through rate on pro-sketch prior to hold (evidence of demand) | OWNER (pre-hold export) |
| Item count after hold shows as expected in MC UI | OWNER — confirm 44 after next fetch |

Export path: MC → Products → All products → download report; Diagnostics page screenshots for flags.

## D. Payhip & email — OWNER figures

| Metric | Value |
|---|---|
| Orders / revenue / refunds (90 days, all products) | OWNER |
| Orders on the 4 verified-count products | OWNER |
| Freebie downloads → email signups | OWNER (Payhip + ESP) |
| Email list size | OWNER |

## E. Pinterest — OWNER export (30 days)

| Metric | Value |
|---|---|
| Impressions / saves / outbound clicks | OWNER |
| Top pin (product, CTR) | OWNER |
| Clicks to digikitpro.shop from pins | OWNER |

## F. How to file the baseline

1. Fill cells above with exports; save exports under `docs/growth-strategy-2026-11/baseline-data/` (owner's local files — do not commit customer data; CSV exports are aggregate, OK).
2. Post the four numbers that matter most in the strategy docs: organic clicks, MC CTR, orders, refund rate.
3. Re-measure at day 30/60/90 against `10-growth-roadmap-90-day.md` gates.

**Until B–E are filled, no SEO/content/feed decision can be called validated.** The repo side is done: builds green, feed truthful (except the flagged caveats awaiting your call).
