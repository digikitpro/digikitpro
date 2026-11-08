# Phase 4 — Complete SEO Audit (2026-11-08)

Environment: live site fetched (homepage + robots.txt reachable; site fully rendered), repo QA suites green ([Repo]: `verify.py` 115/115, `qa_seo.py` 3207 checks / 104 pages / 101 sitemap URLs / 173 sitemap images / 18 articles / 10 HowTo blocks / exits 0). No GSC, no CrUX, no crawl-log access — indexing and Core Web Vitals are **Unknown**, not zero.

## Technical SEO

| Area | Status | Evidence / action |
|---|---|---|
| HTTPS | ✅ | https://digikitpro.shop served; fetched clean |
| robots.txt | ✅ | Allows all; declares 3 sitemaps (sitemap.xml, sitemap.txt, sitemap-images.xml) |
| Sitemap | ✅ structural | 101 URLs; images declared; regenerated on build (`qa_seo` validates invariants, not Google's fetch) |
| Indexing state | ❓ Unknown | No Search Console access — owner must confirm "Indexed" count in GSC Coverage and fix "Crawled – currently not indexed" for thin seasonal pages (Halloween PNGs likely candidates) |
| Canonical URLs | ⚠️ Unverified | Canonicals emitted by build; Google's *selected* canonical unknown without GSC |
| Duplicate pages | ⚠️ Watch | Guides + category + PDP overlap (e.g. portrait guide vs /category/portrait/ vs 3 portrait PDPs) — internal cannibalisation guard needed (see keyword map) |
| Broken links | ✅ QA | `verify.py` link checks pass (115 checks include internal link integrity) |
| Redirects | ⚠️ Unknown | No crawl-log data; spot-check top-20 organic entries after GSC baseline exists |
| Mobile usability | ⚠️ Unknown | Responsive by construction (CSS grid, 4x3 media cards) but not device-tested in this pass |
| Page speed / CWV | ❓ Unknown | No field data; homepage is image-heavy by design (product cards) — owner should run PageSpeed Insights on `/`, `/products.html`, one PDP; target LCP < 2.5s |
| Structured data | ✅ structural / ❓ rich eligibility | Product/Breadcrumb/Article/HowTo emitted & linted (10 HowTo blocks); Google rich-result eligibility only visible in GSC Enhancements |
| XML sitemap freshness | ✅ | Auto-regenerated; `data/indexnow-state.json` present — IndexNow wired for Bing/Yandex (Google ignores IndexNow) |
| Internal linking | ⚠️ | Guides→PDPs strong; homepage→PDP direct; category pages need top-3 article links each |
| OG/Pinterest metadata | ✅ | Cards carry `data-pin-*`; pin buttons live on every card |

## On-page SEO — page-by-page highlights

**Homepage** — strong: H1 "Procreate Brushes for iPad Artists" with clear differentiation ("workflow-organised…free resources"); immediate CTAs; before/after slider *honestly labelled* "Illustrative artwork, not a verified brush-pack demonstration"; featured kits with prices; 51-product browse; workflow cards. Improve: add one paragraph of expert positioning copy (who, why trust) + link to top 3 guides; add `ItemList`/`Organization` sanity check.

**Products.html** — catalogue index; ensure unique meta description and `CollectionPage` schema; check no PDP orphaned (all 51 reachable in ≤3 clicks).

**Category pages** (portrait, line-art, skin-texture, anime, watercolor…) — present; strengthen intro copy (150+ words, expert voice, internal links to 2 best articles + 2 PDPs) to avoid "thin archive" classification.

**PDP template** — good: consistent H1 = pdpH1, alt text enforced (editorial QA), Pinterest metadata, FAQ blocks (HowTo 10×), technical specs table, Payhip CTA. Improve: (a) add 2 plain-language FAQs per PDP answering "will this work for me?"; (b) explicit compatibility line ("iPad + Procreate only — does not work in Photoshop/Clip Studio") near CTA — top cause of returns/refunds for brushes; (c) licence line; (d) "how to install" short blurb linking the install article.

**Blog/guides** — 18 articles, quality above average for niche; HowTo schema present. Weak: keyword-to-intent mapping older titles ("best procreate brushes 2026" lists) need refresh cadence (quarterly).

**About/partner page** — exists; low authority signals; expand with founder story + "why I make these" (supports E-E-A-T for a 2026 AI-saturated SERP).

## Findings by priority

**P0 — fix before any promotion spend**
1. **`pro-sketch-traditional-art-kit` feed highlights leak internal audit caveats** ("Cover and text need owner verification", "Cover and advertised contents require confirmation") — [Repo: `google-merchant-feed.xml`]. Google users would see this verbatim. Owner: resolve `.rar` re-upload (Payhip, high-priority audit item H) **or** exclude the item from the feed until resolved; then rewrite highlights to factual benefit copy. Do not merely sed the wording while the file itself is an RAR.
2. **Unconfirmed counts remain for 7 products** — [Repo: audit register]. Feed copy is hedge-free but sources unverified; owner to confirm the 7 remaining listings (Deliverable 5, column "action").

**P1 — this month**
3. `google_product_category: 500046` — verify the taxonomy ID in Merchant Center UI; cannot be validated offline. Wrong category = restricted serving.
4. Paid products **excluded from feed**: `morocco-7-day-itinerary` ($5), `procreate-portrait-masterclass-ebook` ($19) — confirm exclusion is deliberate; if not, add (they are legitimate digital goods; eBook especially — it converts informational traffic).
5. Cannibalisation guard: define one canonical target per intent cluster (see `03-keyword-architecture.csv` `target_page`); portrait cluster has 4 competing URLs.
6. Category-page thin copy (see above); meta descriptions audit for the 5 highest-impression category pages.
7. Install-friction: every PDP needs the 3-line "open .brushset in Safari → Copy to Procreate" steps + link (this single addition historically reduces "doesn't work" tickets — competitor support forums agree on the pattern).

**P2 — 30–60 days**
8. Capture baselines: GSC 16-month export (queries, pages, CTR, position, countries), MC 90-day (impressions, clicks, CTR by product), Pinterest 30-day, Payhip orders. Without these, every later change is guesswork. (Owner action — credentials not available here.)
9. Core Web Vitals + mobile test via PageSpeed Insights on 10 representative templates; fix LCP (preload hero WebP, `fetchpriority=high` on first card image).
10. Internal-link pass: category pages → top 3 articles; articles → 1 PDP each (see column `target_page`); fix orphaned older posts (2025 kitchen-sink list).
11. Review/social-proof block on PDPs (even 3 founding-buyer quotes beat zero trust signals vs Etsy competitors).

**P3 — hygiene**
12. Quarterly refresh of the 2026 list articles; date-stamp and re-validate "best" claims; keep "252+/43" counts synced to `products.json` on every rebuild (QA enforces).
13. IndexNow: keep `data/indexnow-state.json` updated; ignore Google (it doesn't consume it).

## Addendum — 2026-11-08 (same day, PR #81)

P0-1 is **resolved by exclusion, not rewording**: `pro-sketch-traditional-art-kit` was removed from `google-merchant-feed.xml` via `FEED_HOLDS` in `tools/merchant_feed.py` (feed now 44 items) until the owner re-uploads a verified ZIP on Payhip and confirms the cover. The P0-1 wording above describes the state found at audit time; the audit-caveat highlights are no longer emitted. A further nine items carry buyer-visible confirmation-caveat highlights (register item D) — left untouched pending owner decision.

## What was NOT audited

Core Web Vitals field data · mobile rendering on-device · GSC canonical selection · backlink profile (no third-party tool access here; use free Ahrefs Webmaster Tools) · Merchant Center diagnostics UI · Payhip fulfilment reliability · actual indexing of the 101 sitemap URLs.
