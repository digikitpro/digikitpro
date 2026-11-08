# Growth baseline — November 2026 (template + repo-derived metrics filled)

Owner-side gap flagged throughout: **nothing here changes until your GSC/MC/Payhip/Pinterest exports land.** This file is the intake point; fill every cell marked `OWNER` and the strategy becomes measurable. Repo-derived figures (all re-verified 2026-11-08 on `arena/09bf8858-digikitpro` after the PR #81 feed hold):

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

## B. Google Search Console — OWNER export (16 months)

| Metric | Value |
|---|---|
| Total impressions / clicks / CTR / avg position | OWNER |
| Indexed vs submitted (101 URLs) | OWNER |
| Top 20 queries (impressions, clicks, position) | OWNER |
| Top 10 pages by clicks; 10 striking-distance (pos 5–20) | OWNER |
| Coverage issues ("Crawled – currently not indexed") | OWNER |
| Country split (US vs other) | OWNER |

Export path: GSC → Performance → Search results → Export (CSV), last 16 months; Coverage → Export.

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
