# GSC baseline — November 2026 (owner exports, analyzed 2026-11-08)

**Sources (your exports; not committed — content only, no raw customer data):**
- `Filters.csv` — Web search, **Last 3 months**; range 2026-09-12 → 2026-11-06.
- `Chart.csv` — daily clicks/impressions/position.
- `Countries.csv`, `Devices.csv`, `Pages.csv`, `Queries.csv`, `Search appearance.csv`.
- Indexing report: `Chart-2.csv` (range 2026-09-12 → 2026-10-23, "All known pages" from sitemap),
  `Critical issues.csv`, `Non-critical issues.csv` (empty), `Metadata.csv` (Sitemap: All known pages).

## Headline numbers

| Metric | Value |
|---|---|
| Clicks (3 months) | **0** |
| Impressions | **294** (peak 12 on 2026-10-12; ~5.3/day) |
| Days with ≥1 impression | 50 of 56 |
| Weighted avg position (impr-weighted) | **≈10.0** |
| Indexed pages | **6** (was 9 on Sep 15 → lost 3, flat at 6 since Sep 22) |
| Known pages (processed from sitemap) | **~12** of 101 submitted |
| Product pages / PDPs / collections with impressions | **0** |
| Rich-results impressions | none in export |

**Pages with impressions (all blog; all 0 clicks):**
how-to-choose-procreate-brushes 109 @ 8.59 · best-procreate-brushes-for-anime 78 @ 8.41 · realistic-skin-in-procreate 31 @ 8.0 · make-digital-art-look-traditional 27 @ 10.33 · best-line-art 16 @ 28 · best-portraits 15 @ 12.33 · blending-brushes 13 @ 10.31 · realistic-hair 10 @ 7.6

**Queries:** all 1–2 impressions; positions 10 (*procreate brushes difference*), 42 (*best lineart brush procreate*), 29 (*procreate skin brush*), 51 (*procreate portrait brushes*), 62–71 (*procreate line brush* cluster).

**Devices:** desktop 156 / mobile 110 / tablet 28. **Countries:** US 113 (38%), UK 30, Canada 14, Australia 12, India 10, 53 countries total.

## What the evidence supports (inference, labelled as such)

1. **[Evidence]** The site's own chain is clean: `SITE_URL=https://digikitpro.shop` (tools/core.py), canonicals, sitemap URLs, robots.txt sitemap lines, search.html + 404.html are `noindex`, category pages carry real 250–390-word unique intros, articles already link to PDPs (2–15 links each), and every impression-earning page's title is keyword-front and benefit-led. → *On-page code is not the blocker; do not churn titles or articles right now.*
2. **[Evidence]** `netlify.toml` ships 301s for http→https, www→apex, /index.html→/; but its own comment notes GitHub Pages **“Enforce HTTPS: https_enforced=false — enable it”**. Deploys push to **GitHub Pages** on `main` (deploy.yml), CNAME = digikitpro.shop. → *http:// URLs can be served 200 by GitHub Pages, which lets Google crawl a duplicate http host — exactly what the export shows (Pages.csv URLs are `http://`).*
3. **[Evidence]** Coverage knows only ~12 URLs (6 indexed + 6 not) vs 101 submitted, and 3 indexed pages were lost between Sep 15–22 — consistent with Google resolving http-vs-https duplication site-wide for a young property, not with quality collapse. Validation was started for all 3 critical issues.
4. **[Evidence]** "Crawled – currently not indexed" ×1 — the only issue that isn't explainable by host canonicalization; page identity is not in the export. Likely one of: a soft-dupe category page, an http duplicate, or a thin page. Needs URL Inspection.
5. **[Evidence]** Products/pages get 0 impressions; blog captures 100% of the tiny demand (~83% sits on 4 URLs). The store's commercial surface is effectively uncounted by Google today.
6. **[Unknown]** Which verified property you exported (Domain vs http URL-prefix vs https URL-prefix). The http:// URLs in Pages.csv strongly suggest an http-scoped property or a duplicate-crawl situation. *This is the single config fact that decides most of the recovery.*

## Owner action plan (Google/GitHub switches — not code)

Priority order; ~30–45 minutes total:

1. **GitHub Pages Enforce HTTPS** — repo Settings → Pages → check "Enforce HTTPS". If it stays disabled (e.g. the "not available" grey state), wait for the certificate to re-issue (usually <24h) or re-save Pages settings, then check again. This stops http:// 200s.
2. **GSC properties** — GSC → Settings → Add property: add a **Domain property** `sc-domain:digikitpro.shop` (DNS) *or* the `https://digikitpro.shop` URL-prefix. Keep the http property for history but treat it as legacy.
3. **Resubmit the sitemap** under the new property: `sitemap.xml` (and `sitemap-images.xml`).
4. **Coverage reconciliation** — in the new property, list the 6 indexed / 6 not-indexed URLs; run URL Inspection on: homepage, products.html, bundles.html, freebies.html, collections pages, and the top PDPs (portrait-skin, portrait-mastery-kit, essential-line-art, ultimate-portrait-mastery-bundle) — **Request Indexing** for each. Identify the 1 "Crawled – currently not indexed" page and improve/consolidate it.
5. **Leave Validation = Started** on the three critical issues; don't click further magic buttons.
6. **28-day re-read** — re-export Performance + Indexing after ~2026-11-22 and ~2026-12-06. Success signals in order: known pages > 40 · indexed > 25 · product surfaces appear in impressions · clicks > 0 (expect single digits at first). If known pages stays < 20, the property/scope is still wrong.
7. **Do NOT** rewrite the 8 blog articles' titles yet; reassess CTR only after indexing and clicks appear.

## Dashboard cells this document replaces with real data

GSC baseline: clicks **0** · impressions **294** · CTR **0%** · weighted position **≈10** · indexed **6/101 known ~12** · top-4 URLs carry **245 of 294 (83%)** impressions · queries & devices/countries splits as above. Any prior strategy-pack cells marked "OWNER" for these = answered.

## What we still don't know

Which property you exported; why exactly 3 pages dropped Sep 19→22 or which page holds "Crawled – currently not indexed"; whether HTTPS was enforced at crawl time; CTR-position data beyond 28-day minimums. Do not conclude anything from one 28-day window either way.
