# DigiKitPro — Site Audit & Sales-Engine Implementation Plan

**Audited:** commit `bec90f7` (`Auto-sync: update Payhip catalog`) + the live build at
`https://digikitpro.github.io/digikitpro/index.html` (verified byte-identical to the repo build).
**Audited by:** reading every generator in `tools/`, the full `data/products.json` (51 products),
all 10 shipped page types, `css/style.css`, `js/main.js`, `js/translate.js`, `js/search-index.js`,
both GitHub Actions workflows, `robots.txt`, `sitemap.xml`, `feed.xml`, `netlify.toml`.

> **Rule followed throughout:** nothing in this document invents sales numbers, reviews,
> traffic, or trend statistics. Where a number appears it is counted from the repository.
> Where a metric is unknown it is written as **"unknown — no instrumentation exists yet"**,
> because that is literally the case (see Problem 7).

---

## PART 1 — CURRENT ARCHITECTURE DISCOVERED

### 1.1 What the site actually is

A **100 % static, generator-built multi-page site**, deployed to GitHub Pages.
There is **no backend, no database, no framework, no build-time JS toolchain.**

```
data/products.json ──┐
content/blog/*.md ───┼──► tools/build.py ──► 100+ committed .html files + sitemap + feeds + search index
tools/core.py ───────┘         (Python 3, stdlib only)
```

| Layer | Reality |
|---|---|
| Source of truth | `data/products.json` — 51 products, 329 KB, 27 fields each |
| Generator | `tools/build.py` → `core.py` (570 ln) + 6 page modules (~1,500 ln total) |
| Output | HTML is **committed to the repo**; the repo root *is* the deploy artifact |
| Hosting | GitHub Pages via `.github/workflows/deploy.yml` (build on every push to `main`) |
| Payments | External — Payhip (`payhip.com/digikitpro`), all CTAs are `target="_blank"` outbound links |
| Email capture | FormSubmit → `digikitprostudio@gmail.com` (AJAX, honest success/pending/error states) |
| Analytics | GA4 `G-5MFQFHNB6B`, **`config` call only — zero custom events** |
| Client JS | `js/main.js` 14.4 KB (nav, search, filters, gallery, forms) · `js/translate.js` (Google Translate) · `js/search-index.js` 35 KB generated |
| CSS | `css/style.css` 34.9 KB, single file, CSS custom properties, mobile-first |
| Fonts | Self-hosted woff2 (Playfair Display + Manrope), `font-display:swap`, preloaded |
| Images | 402 files / 24 MB WebP in 3 variants (`-card`, full, `-thumb`) + `srcset` |
| Automation | `sync-payhip.yml` (daily 06:30 UTC) → `payhip_sync.py` → `seo_engine.py` → rebuild → auto-commit |

### 1.2 Page inventory (all verified present)

| Page | Path | State |
|---|---|---|
| Homepage | `index.html` | 10 sections, 1,156 visible words, 27 images, 8 Payhip CTAs |
| Catalog | `products.html` | 51 cards, 14 filter chips, flat single grid |
| Bundles | `bundles.html` | 6 bundles, hand-ordered |
| Freebies | `freebies.html` | 4 free products |
| Articles index | `blog.html` | 18 articles |
| Article pages | `blog/<slug>/` | 18, with FAQPage + HowTo JSON-LD |
| Product pages | `products/<slug>/` | 51 |
| Category SEO pages | `category/<slug>/` | **10 of 13 categories** (no Bundles / Guides & eBooks / Other) |
| Seasonal hubs | `season/halloween/`, `season/christmas/` | 2, date-gated bands on homepage |
| About (+ FAQ + Contact) | `about.html` | FAQ & contact are **anchors**, not pages |
| Search | `search.html` + `⌘K` overlay | Client-side, 2-char minimum |
| Privacy / Terms / 404 | `privacy.html`, `terms.html`, `404.html` | Present |
| **FAQ page** | — | **MISSING** (only `about.html#faq`) |
| **Contact page** | — | **MISSING** (only `about.html#contact`) |
| **Thank-you page** | — | **MISSING** (signup ends with an inline message) |
| **Brush Finder** | — | **MISSING** |

### 1.3 What is ALREADY WORKING (do not touch)

| # | Asset | Why it's valuable |
|---|---|---|
| W1 | **`data/products.json` as single source of truth** | Rare discipline. Every page, card, sitemap entry and schema node derives from it. All new work must respect it. |
| W2 | **Real, verified product data** | Prices, `.brushset` specs, ZIP sizes, Payhip URLs scraped from the live store on 2026-08-11. Nothing invented. All 51 products have `faqs`, `perfectFor`, `features`, `included`, `technical`, `related`, `alt`, `keywords` populated (100 %). |
| W3 | **Technical SEO** | Per-page title/meta, canonicals, OG + Twitter, `Product`+`Offer` JSON-LD with real prices, `FAQPage`, `HowTo`, `BreadcrumbList`, `Organization`, `WebSite`+`SearchAction`, `sitemap.xml` (76+ URLs, image sitemap), `sitemap.txt`, `feed.xml`, IndexNow-ready, Google/Bing/Yandex verification. |
| W4 | **18 substantive articles** | Real technique content with step-by-step HowTo schema. This is the traffic engine that already exists. |
| W5 | **10 hand-written category landing pages** | Unique intros, guide cross-links — genuine search-intent pages, not thin AI filler. |
| W6 | **Premium dark + gold design system** | Playfair/Manrope, `--gold:#C9A86A`, coherent card/badge/button vocabulary. Strong, ownable, artist-premium. **Preserve.** |
| W7 | **Performance engineering** | WebP + `srcset` + `sizes` + `loading=lazy` + `fetchpriority=high` on LCP only, self-hosted fonts, `preconnect` to Payhip, zero frameworks, 14 KB JS. Homepage references only 1.66 MB of assets. |
| W8 | **Failure resilience** | Broken-image → branded SVG fallback; global JS error boundary bar; `noscript` notice; `file://` link rewriting; popup-blocker fallback so **every** Buy button reaches Payhip. |
| W9 | **Honest email capture** | FormSubmit AJAX with three truthful states, never fakes success. |
| W10 | **Date-gated seasonal bands in the generator** | Halloween/Christmas promos can never go stale on the live homepage. |
| W11 | **Badge hygiene** | `HIDDEN_BADGES = {"new","masterclass"}` — the generator already refuses to print labels that age badly. |
| W12 | **Deploy + Payhip auto-sync CI** | Owner edits JSON in the browser, site rebuilds itself. Low-friction content ops. |

### 1.4 What is CONFUSING

| # | Finding | Evidence |
|---|---|---|
| C1 | **The flagship is invisible.** `master-library-2000-brushes` (2,000+ brushes, $19 — the highest-value product in the store) appears **0 times** in `index.html`. | `grep -c "master-library" index.html` → `0`. Cause: `build_home()` sorts bundles by price **ascending** and slices `[:4]`, so the homepage shows the $5 palette bundle, $8 Christmas, $15 portrait bundle, $15 Master Vault. |
| C2 | **No product hierarchy.** 51 products, **28 priced at exactly $5.00**, presented as one undifferentiated grid. Nothing answers "what should I buy first?" | Price histogram: `$5×28, Free×4, $10×4, $8×3, $7×3, $15×2, $19×2, $9×2, $4×2, $20×1` |
| C3 | **"Other" is a 17-product dead-end bucket** (33 % of catalog) with no category page; the chip deep-links to `products.html#cat-Other`. | `Counter(category)` → `Other: 17` |
| C4 | **Positioning dilution.** 9 products have no Procreate/iPad connection at all — 5 planners/journals, a Morocco travel itinerary, KDP Canva templates, a Japanese watercolour *asset* pack, a Halloween PNG pack. A Procreate artist filtering the catalog sees "Discover Morocco in 7 Days: Marrakech to Sahara Itinerary" and "Digital 2026 ADHD Balanced Mind Planner". | Keyword scan of name+short+requirements |
| C5 | **"Trending" is pseudo-random, not demand-driven.** `build_home()` rotates the trending pool by `date.today().toordinal() % len(pool)`. It shows a different 4 products every day with no relationship to what anyone is searching or buying. | `pages_main.py`, trending block |
| C6 | **Daily rotation makes every deploy diff the homepage.** Rebuilding today moved the Masterclass card and re-shuffled the grid → 93 files changed for a no-op build. Bad for git hygiene and it hands Google a different homepage every crawl. | Verified by running `python3 tools/build.py` on a clean tree |
| C7 | **FAQ and Contact are anchors, not pages.** They can't be linked from the footer as destinations, can't rank, and can't carry their own schema cleanly. | `about.html#faq`, `about.html#contact` |
| C8 | **Bundle value is asserted, not itemized.** `bundleContents` is populated for **1 of 6** bundles, so 5 bundle pages can't show a "what's inside / what it's worth" table. | Field audit: `bundleContents: 1/51` |
| C9 | **Data hygiene bug in `requirements`.** `portrait-skin-brushes-procreate.requirements` mixes marketing lines into a spec list, which renders on the live PDP as requirements reading *"Bring Your Portraits to Life"*, *"Instant Download"*. | Verified in rendered HTML |

### 1.5 What PREVENTS VISITORS FROM BUYING

| # | Blocker | Mechanism |
|---|---|---|
| B1 | **No discovery path.** Search is keyword-only; filters are category-only. There is no route from *"I paint portraits and my skin looks plastic"* → the right $5 pack. The visitor must self-diagnose across 51 cards. |
| B2 | **Free funnel skips the email.** Free PDPs' primary CTA is `Get Free Download ↗` → straight to Payhip. The newsletter block is at the page bottom, unrelated to the freebie. **No thank-you page, no post-download starter offer, no sequence hook.** The single best lead magnet in the store produces zero list growth by design. |
| B3 | **No upsell or comparison anywhere.** PDPs show only `Related Products` (4 cards). There is no "$7 single pack **vs** $19 Master Library" framing, no bundle upgrade from an entry pack, no portrait-tools → Masterclass cross-sell. AOV is capped at whatever the visitor happened to land on. |
| B4 | **Product pages sell specs, not results.** Galleries are Payhip *cover art* (product-marketing images), not `brush → stroke → application → finished artwork`. No stroke swatches, no before/after, no "what can I create with it" section. 9 products have fewer than 2 gallery images. |
| B5 | **Zero social proof, and no architecture to add it.** No reviews, no testimonials, no customer artwork, no empty-state placeholder. (Correctly, nothing is faked — but the *slot* doesn't exist either, so proof can't be dropped in later without a rebuild.) |
| B6 | **Commercial-usage answer is buried.** The licence question ("can I sell what I make?") is answered only inside the FAQ `<details>` and on `terms.html`. It's a real purchase objection for working artists and it's below the fold, collapsed. |
| B7 | **Hero CTA sends intent into the flat grid.** "Explore Brushes" → `products.html` = 51 cards + 14 chips. Highest-cognitive-load page on the site is the primary hero destination. |
| B8 | **No conversion instrumentation → no optimisation is possible.** No `product_view`, no `product_buy_click`, no `outbound_payhip_click`. The owner cannot answer "which product page gets traffic but no sales?" — the single most profitable question in the business. |

### 1.6 What CAN be improved without rebuilding

Everything in Phase 1 below. The generator architecture is the reason: adding a section = one
function in `tools/`, adding a page = one module + one `write()` call. No framework migration,
no data migration, no hosting change.

### 1.7 What functionality can be added SAFELY (static-only, GitHub-Pages-safe)

Client-side JS reading a **generated data file** (`js/finder-index.js`, same pattern already
proven by `js/search-index.js`). This covers: Brush Finder, tier/hierarchy rendering, upgrade
panels, event tracking, feedback capture, A/B variants. No server, no keys, no CORS, no cost.

### 1.8 What should NOT be changed

- The visual identity (dark/gold, Playfair+Manrope) — it reads premium and artist-focused.
- `data/products.json` as the source of truth, or the Payhip auto-sync contract that writes to it.
- The existing 18 articles and 10 category pages (they are the organic-traffic asset).
- JSON-LD schema, sitemap, feeds, verification tokens.
- The resilience layer in `main.js` (image fallback, error boundary, popup fallback).
- Any product's existence or price. **Nothing is removed without owner approval.**
- The static-only constraint. GitHub Pages compatibility is a hard requirement.

---

## PART 2 — TOP 10 CONVERSION PROBLEMS (ranked by revenue impact)

| # | Problem | Revenue mechanism | Severity |
|---|---|---|---|
| **1** | **No product discovery / recommendation engine.** Nothing answers "what should I buy?" for a catalog of 51 items, 28 identically priced. | Directly caps conversion rate on all cold traffic (social, Pinterest, SEO). The visitor must do the merchandising work. | 🔴 Critical |
| **2** | **The $19 flagship Master Library is absent from the homepage.** Highest-AOV product, zero exposure on the highest-traffic page. | Caps AOV at ~$5–$8. Moving even a small share of buyers from a $5 pack to the $19 library roughly quadruples order value. | 🔴 Critical |
| **3** | **Zero conversion tracking.** No custom GA4 events; outbound Payhip clicks untracked. | The business is unmeasurable. No conversion rate, no product-level revenue attribution, no way to know which optimisation worked. Blocks every other item on this list from being *proven*. | 🔴 Critical |
| **4** | **The free funnel captures no email.** Freebie → Payhip directly; no thank-you page; no starter offer; no sequence entry point. | Kills list growth, kills the entry→bundle→library ladder, kills repeat purchase. The freebie currently works as a *cost* with no captured asset. | 🔴 Critical |
| **5** | **No upsell / comparison architecture on product pages.** Only 4 "related" cards. | Caps AOV and blocks the entry→bundle→flagship ladder on the page where purchase intent is highest. | 🟠 High |
| **6** | **Product pages show cover art, not results.** No stroke previews, no before/after, no finished-artwork demonstration. | "Need more examples" is the #1 reason digital-art buyers abandon. Directly suppresses PDP→buy-click rate. | 🟠 High |
| **7** | **Privacy policy contradicts the deployed site.** `privacy.html` states *"sets no tracking cookies and includes no third-party analytics by default"* while GA4 loads on every page and Google Translate writes `googtrans` cookies. | Trust + legal exposure (GDPR / ePrivacy / CCPA). A single complaint or a marketplace review can cost more than a month of sales. | 🟠 High |
| **8** | **Positioning dilution: 9 non-Procreate products share the catalog, filters, search and "Trending" rotation.** | Weakens the "professional Procreate tools" promise at exactly the moment a new visitor decides whether to trust the store. Also pollutes internal-link equity for the money pages. | 🟡 Medium-High |
| **9** | **No social proof and no proof *slot*.** No reviews, testimonials, or customer-artwork section — and no empty-state architecture to populate later. | First-time buyers on a $5–$19 impulse purchase rely heavily on peer evidence. Absence is a silent conversion tax. | 🟡 Medium-High |
| **10** | **Homepage content rotates daily and every deploy diffs 93 files.** | Unstable signals on the most important URL, plus operational noise that makes real changes hard to review. | 🟡 Medium |

**Also fixed in this pass (not top-10 but real):** `requirements` data pollution (C9),
hero CTA pointing into the flat grid (B7), FAQ/Contact not being pages (C7),
bundle contents not itemized (C8), 5 of 13 categories without SEO pages.

---

## PART 3 — TOP 10 OPPORTUNITIES RANKED BY REVENUE IMPACT

Ranked by `(affected traffic × expected lift × order value) ÷ build cost`. All lifts are
**hypotheses to be measured**, not claims — item #1 exists precisely so they can be tested.

| # | Opportunity | Funnel stage | Expected impact | Cost | Verdict |
|---|---|---|---|---|---|
| **1** | **Brush Finder — "Find My Brushes"** (4 questions → personalised starter + bundle + Master Library + Masterclass + freebie) | Discovery → First purchase | Converts undecided cold traffic that currently bounces off a 51-card grid. Also becomes a linkable, shareable, SEO-ownable asset ("Procreate brush quiz"). Generates the *choice data* the owner has never had. | M (1 data file + 1 JS + 1 page) | **BUILD FIRST** ✅ done |
| **2** | **Master Library flagship band on homepage + PDP upgrade panel on every non-flagship product page** | AOV / upsell | Highest-leverage AOV move available: $5 → $19 is a 3.8× order value with zero new inventory. The comparison is honest and arithmetic ("2,000+ brushes for the price of four single packs"). | S | ✅ done |
| **3** | **Event-tracking layer** (14 events, GA4 + privacy-conscious local session log) | Intelligence | Unlocks measurement for #1, #2, #4 and every future test. Without it nothing else can be validated. Also produces the "100 views, 0 sales" problem report the brief asks for. | S | ✅ done |
| **4** | **Email-first freebie funnel + thank-you page with starter offer** | Email → First purchase | Turns the store's best lead magnet into list growth *and* an immediate $5–$8 starter offer on the page with the highest goodwill. Thank-you page also becomes the sequence entry point. | S–M | ✅ done |
| **5** | **"What do you create?" craft grid on homepage + Brush Finder entry in nav** | Discovery | Routes intent before the catalog. Replaces "Explore Brushes → 51 cards" with "Portraits → 3 relevant products". Cheap, high-visibility, mobile-friendly. | S | ✅ done |
| **6** | **Product hierarchy (`tier`: free / entry / bundle / flagship / education) rendered across homepage, catalog, finder and PDPs** | Discovery → AOV | Gives the catalog a spine: Free → $5 specialist → $10–15 bundle → $19 library → $19 education. Same inventory, ordered by intent. | S | ✅ done |
| **7** | **"Why didn't you buy?" lightweight feedback** (once per session, dismissible, non-blocking, GA4 + optional endpoint) | Intelligence | Cheapest possible qualitative signal. If "Not sure which brush I need" dominates → Finder is right; if "Need more examples" dominates → PDP media is the next build. | S | ✅ done |
| **8** | **SEO landing pages for high-intent queries not yet covered** (Procreate pencil brushes, texture brushes, Procreate Dreams / animation brushes, best brushes for beginners as a *commercial* page, bundle comparison page) | Traffic | 18 articles + 10 category pages already exist; the gap is commercial-intent pages that carry products, not just teach. | M | Phase 3 |
| **9** | **Social-proof architecture with honest empty states + artist submission form** (permission-gated, never auto-published) | Trust | Slot must exist before proof can be added. Zero fabrication: sections render only when data is present. | M | Phase 2/5 |
| **10** | **Deterministic homepage + category separation of Procreate art tools vs planners/lifestyle** | Trust / positioning | Protects the "professional Procreate tools" promise without deleting anything (planners move to their own labelled section + page). | S | ✅ done (non-destructive) |

**Explicitly NOT built** (fails the "will this make money?" test right now):
AI chatbot · SaaS-style customer dashboard · accounts/logins · on-site checkout · fake counters,
urgency or scarcity · animated hero gimmicks · thousands of thin AI SEO pages · a database.

---

## PART 4 — RECOMMENDED PHASE 1 ARCHITECTURE

**Principle: extend the generator, never hand-edit generated HTML. Everything stays static.**

```
                       ┌──────────────────────────────────────────┐
                       │  data/products.json   (UNCHANGED — Payhip│
                       │                       sync still owns it)│
                       └────────────────┬─────────────────────────┘
                                        │
   data/discovery.json  ────────────────┤   NEW: tier / craft / improve /
   (hand-authored, evidence-based,      │   level / style / priority per product
    derived from real tags+categories)  │   + the 4 question sets + craft cards
                                        ▼
                            ┌───────────────────────┐
                            │  tools/build.py       │
                            │  + pages_finder.py    │  NEW
                            │  + core.py helpers    │  EXTENDED
                            └───────────┬───────────┘
              ┌─────────────────────────┼──────────────────────────────┐
              ▼                         ▼                              ▼
   index.html (hero trust,     find-my-brushes.html          js/finder-index.js  NEW
   craft grid, flagship band,  thank-you.html       NEW      (window.DKP_FINDER —
   tiered catalog)                                           same pattern as search-index.js)
   products/<slug>/ (upgrade panel, licence line, feedback mount)
              │
              ▼
   js/analytics.js  NEW  ──► GA4 gtag (if present) + privacy-conscious local session log
   js/finder.js     NEW  ──► scoring engine, results rendering, events
   js/feedback.js   NEW  ──► "what stopped you today?" (once/session, dismissible)
```

**Design decisions:**

1. **`data/discovery.json` is a separate file, not new fields in `products.json`.**
   `payhip_sync.py` writes to `products.json`; keeping discovery data apart means the daily
   auto-sync can never clobber the merchandising model, and a newly synced product simply gets
   safe defaults until the owner tags it.
2. **The Brush Finder is server-rendered first, JS-enhanced second.** All four questions and
   every option are real HTML (crawlable, indexable, works without JS via a grouped-catalog
   fallback). JS intercepts submit and renders results instantly — no round trip, no framework.
3. **Scoring is transparent and relevance-first, not price-first.** Weighted match on
   craft (40) + improvement goal (30) + style (15) + level (10) + editorial priority (≤5),
   then tier-aware presentation. The engine never recommends the most expensive item by default;
   the Master Library is offered as a clearly-labelled *separate* "want everything?" step.
4. **Tracking is dual-channel.** `gtag('event', …)` when GA4 is loaded, plus a local
   session summary in `localStorage` (no PII, no cross-site identifier, no new cookies) so the
   owner has data even before GA4 is configured, and so a future serverless collector can be
   dropped in without changing any page.
5. **Nothing fabricates.** No review counts, no "X artists bought this", no invented trend data.
   Sections that need owner-supplied proof render only when data exists.

---

## PART 5 — EXACT FILES CHANGED

| File | Change | Risk |
|---|---|---|
| `tools/core.py` | Nav gains **Find My Brushes**; `head()` loads `js/analytics.js` + `js/finder.js`; new helpers `hero_trust()`, `craft_grid()`, `flagship_band()`, `upgrade_panel()`, `licence_line()`, `tier_of()`; `trust_band()` keeps worldwide copy; **privacy policy text corrected** to disclose GA4 + Google Translate; `newsletter()` gains `source`/`lead` hidden fields | Medium — touches every page via header/head |
| `tools/pages_main.py` | Homepage: hero trust row, **What do you create?** grid, **Master Library flagship band**, tier-ordered sections, **deterministic** trending (rotation removed); `products.html`: tier headings + Procreate-art vs Planners & Lifestyle separation; `freebies.html`: **email-first funnel**; `bundles.html`: flagship first | Medium |
| `tools/pages_product.py` | **Upgrade / comparison panel** ("$7 single vs $19 Master Library"), licence line above the fold, install-steps block, feedback mount, `requirements` hygiene filter | Medium |
| `tools/pages_finder.py` | **NEW** — builds `find-my-brushes.html`, `thank-you.html`, `js/finder-index.js` | None (new) |
| `tools/pages_misc.py` | Sitemap + `sitemap.txt` gain the new URLs | Low |
| `tools/build.py` | Registers `pages_finder` | Low |
| `css/style.css` | New component styles (trust row, craft grid, flagship band, finder, upgrade panel, feedback sheet, thank-you) — appended, existing rules untouched | Low |
| `js/analytics.js` | **NEW** | None |
| `js/finder.js` | **NEW** | None |
| `js/feedback.js` | **NEW** | None |
| `data/discovery.json` | **NEW** | None |
| `docs/AUDIT-AND-PLAN.md` | **NEW** (this file) | None |
| `README.md` | Documents the new files, the event list and the email-automation contract | Low |

**Deliberately NOT changed:** `data/products.json`, `content/blog/*.md`, `js/main.js`,
`js/translate.js`, `js/search-index.js` (regenerated only), all 18 article pages' copy,
`robots.txt`, both workflows, `netlify.toml`, every image.

---

## PART 6 — NEW FILES / COMPONENTS

### New files
| Path | Purpose |
|---|---|
| `data/discovery.json` | Merchandising model: product tiers, craft/improve/level/style mappings, editorial priority, the 4 finder questions, the 7 craft cards, tier definitions |
| `js/analytics.js` | `dkp.track(name, params)`; auto-binds every specified event; local privacy-conscious session log |
| `js/finder.js` | 4-question engine, scoring, result rendering, `brush_finder_*` / `recommendation_clicked` events |
| `js/feedback.js` | "What stopped you from choosing a brush today?" — once/session, dismissible, non-blocking |
| `find-my-brushes.html` | Generated. The Brush Finder (crawlable) |
| `thank-you.html` | Generated. Post-signup page: free download links + starter offer + Master Library |
| `js/finder-index.js` | Generated. `window.DKP_FINDER` — the slim data the JS engine needs |
| `docs/AUDIT-AND-PLAN.md` | This document |

### New components (visual vocabulary reuses existing tokens — no new design language)
`hero-trust` · `craft-grid` / `craft-card` · `flagship-band` · `tier-head` · `upgrade-panel` ·
`finder-*` (progress, options, result, why) · `feedback-sheet` · `thanks-*` · `licence-line` ·
`install-steps`

---

## PART 7 — BACKEND / SERVERLESS REQUIREMENTS

**Phase 1 requires NO backend.** Everything ships as static files on GitHub Pages.

| Capability | Phase 1 solution | Needs a backend? |
|---|---|---|
| Brush Finder | Generated data + client JS | ❌ No |
| Event tracking | GA4 (already configured) + `localStorage` session log | ❌ No |
| Email capture | FormSubmit (already live) | ❌ No |
| Feedback capture | GA4 event + optional `DKP.feedbackEndpoint` (empty = off) | ❌ No (optional later) |
| Thank-you page | Static page, query-string personalised (`?lead=…`) | ❌ No |

### Later phases — what would need a backend, and the cheapest honest option

| Feature | Why it needs a server | Cheapest practical option | Keys / env vars | GitHub Pages stays frontend? |
|---|---|---|---|---|
| **Email automation sequences** (Emails 1–5) | A static site can only *collect* an address; drip sequences need an ESP | **MailerLite or Brevo free tier** — embed their form action URL in `tools/core.py` (`EMAIL_ENDPOINT`). Zero code. | None in the frontend (ESP form URLs are public by design) | ✅ Yes |
| **Own-collected analytics** (if GA4 is dropped) | Needs an ingest endpoint + storage | **Cloudflare Workers + KV** (free tier: 100 k req/day) or **Vercel Edge + Upstash** | `ANALYTICS_COLLECTOR_URL` (public, rate-limited) | ✅ Yes |
| **Trend Radar** (§11–15) | Needs scheduled scraping/API calls + scoring + storage; must never expose API keys | **GitHub Actions cron** (already the pattern used by `sync-payhip.yml`) writing a report to a **private** repo/branch or a Google Sheet. Free. | `REDDIT_CLIENT_ID/SECRET`, `YOUTUBE_API_KEY`, `SERPAPI_KEY` as **repo secrets** | ✅ Yes — output is admin-only, never public |
| **Sales Intelligence Dashboard** (§16) | Needs Payhip order data + GA4 data joined | **GA4 Data API + Payhip CSV export** → GitHub Action → static **`/admin/` page behind GitHub Pages auth** (or a private repo Pages site). Never on the public site. | `GA4_PROPERTY_ID`, `GA4_SERVICE_ACCOUNT_JSON`, `PAYHIP_API_KEY` as secrets | ✅ Yes |
| **Affiliate tracking** (§24) | Needs click→sale attribution | Payhip's own affiliate feature first (it exists and is free); only build custom if Payhip's limits bite | — | ✅ Yes |
| **Artist submissions** (§21) | Needs upload storage + moderation queue | **Cloudflare Workers + R2**, or a **Google Form → Sheet** pipeline (free, zero code, human moderation built in) | `R2_*` as secrets | ✅ Yes |

**Hard rule (already respected, re-asserted):** no API key ever appears in frontend JS.
Anything secret-bearing lives in GitHub Actions secrets or a serverless function.

---

## PART 8 — ANALYTICS EVENTS

Implemented in `js/analytics.js`. All fire through `dkp.track(name, params)` which forwards to
GA4 (`gtag('event', …)`) when loaded **and** appends to a local session log.

| Event | Fires when | Key params |
|---|---|---|
| `homepage_view` | `index.html` loads | — |
| `product_view` | any `products/<slug>/` loads | `product_id`, `product_name`, `tier`, `category`, `price` |
| `category_view` | `category/<slug>/` loads | `category` |
| `bundle_view` | `bundles.html` loads | — |
| `master_library_view` | Master Library PDP loads | `product_id` |
| `masterclass_view` | Masterclass PDP loads | `product_id` |
| `free_download_click` | any CTA on a `free` product | `product_id`, `location` (`card`/`pdp`/`thanks`) |
| `email_signup` | newsletter/freebie form returns a real success or pending state | `source` (`home`/`freebies`/`pdp`/`blog`), `lead_magnet` |
| `product_buy_click` | any Buy/Get CTA on a paid product | `product_id`, `price`, `tier`, `location` |
| `outbound_payhip_click` | **every** click on a `payhip.com` link | `product_id`, `url`, `location` |
| `brush_finder_started` | first question answered | — |
| `brush_finder_completed` | results rendered | `craft`, `improve`, `level`, `style`, `recommended_id`, `match_score` |
| `recommendation_clicked` | any card in the finder result | `product_id`, `slot` (`primary`/`alternate`/`flagship`/`education`/`free`) |
| `upgrade_clicked` | Master Library / bundle upgrade panel CTA | `from_product_id`, `to_product_id`, `price_delta` |
| `craft_card_click` | "What do you create?" card | `craft` |
| `search_query` | search executed (≥2 chars, debounced) | `term_length` only — **the term itself is not stored in the local log** |
| `scroll_depth` | 50 % and 90 % of a PDP | `product_id`, `percent` |
| `feedback_reason` | "What stopped you…" answered | `reason`, `page_type`, `product_id` |

**Privacy rules baked in:**
- No PII, no email addresses, no cross-site identifier, **no new cookies set by DigiKitPro**.
- `navigator.doNotTrack === "1"` → GA4 pushes are suppressed (local counting continues, it is
  first-party and non-identifying).
- `window.DKP.analytics === false` disables everything (single kill-switch for the owner).
- Search terms are measured by *length* only in the local log.
- `privacy.html` is corrected in this changeset to disclose GA4 and Google Translate honestly.

---

## PART 9 — EMAIL AUTOMATION REQUIREMENTS

### Current state (verified)
Forms POST to `https://formsubmit.co/digikitprostudio@gmail.com` (AJAX variant
`formsubmit.co/ajax/...`). **One-time activation is required** — FormSubmit emails the inbox an
"Activate Form" link. Until clicked, submissions are recorded but not delivered.

### What Phase 1 changes
- Every form now carries `_subject`, `_template=table`, plus **`source`** (which page) and
  **`lead_magnet`** (which freebie was promised). This is what makes a sequence possible later:
  the ESP knows *why* the address was collected.
- Signup success redirects to **`thank-you.html`**, which delivers the free download links and
  makes one starter-product offer. This is the top of the ladder.

### Required for the 5-email sequence (owner action, no code)
FormSubmit is a *form relay*, not an ESP — it cannot send drips. The clean integration:

| Step | Action | Where |
|---|---|---|
| 1 | Create a free **MailerLite** (or Brevo/ConvertKit) account, one list: `DigiKitPro Artists` | ESP dashboard |
| 2 | Copy the list's **form action URL** | ESP |
| 3 | Set `EMAIL_ENDPOINT` in `tools/core.py` to that URL (one line), rebuild | Repo |
| 4 | Add the double-opt-in field names the ESP expects (documented in `core.py` next to the constant) | Repo |
| 5 | Build the 5-email automation in the ESP, triggered on subscribe with tag `freebie:<slug>` | ESP |

**No API key is ever placed in frontend code** — ESP form-action URLs are public endpoints by
design and are rate-limited/validated server-side by the provider.

### The sequence (copy ready to paste, no fake urgency)

| # | Timing | Subject | Purpose | Links to |
|---|---|---|---|---|
| 1 | Immediate | **Your free Procreate brushes are ready** | Deliver the promised freebie. Nothing else. | `thank-you.html` / Payhip free product |
| 2 | Day 1 | **3 brushes that can improve your Procreate workflow** | Teach something genuinely useful (pressure curve, one blending brush, one texture brush). | `blog/how-to-choose-procreate-brushes/` |
| 3 | Day 3 | **You probably don't need more brushes** | Counter-intuitive, trust-building. The real problem is organisation, not quantity. Soft Master Library mention. | `blog/procreate-portrait-workflow/` |
| 4 | Day 5 | **The portrait workflow** | Connect education to tools: sketch → ink → blend → texture → finish. | Masterclass + `category/portrait/` |
| 5 | Day 7 | **Build your complete Procreate toolkit** | Master Library offer, with the honest arithmetic (2,000+ brushes vs buying single packs). | `products/master-library-2000-brushes/` |

---

## PART 10 — DATABASE / DATA STRUCTURE

**No database.** GitHub Pages is a static host; a DB would add cost, a backend, keys and a
failure mode — for zero revenue in Phase 1.

The only new data structure is **`data/discovery.json`**, a versioned, hand-authored
merchandising model:

```jsonc
{
  "version": 1,
  "tiers": [                       // the product hierarchy (Level 1→5 from the brief)
    { "id": "free",      "level": 1, "label": "Free",       "cta": "Get Free Procreate Brushes" },
    { "id": "entry",     "level": 2, "label": "Specialist packs", "range": "$4–$9"  },
    { "id": "bundle",    "level": 3, "label": "Bundles",          "range": "$10–$20" },
    { "id": "flagship",  "level": 4, "label": "Master Library"    },
    { "id": "education", "level": 5, "label": "Masterclass & guides" }
  ],
  "questions": [ /* craft, improve, level, style — id/label/hint each */ ],
  "crafts":    [ /* 7 homepage "What do you create?" cards + landing href */ ],
  "catalog": {                     // keyed by product slug
    "portrait-skin-brushes-procreate": {
      "tier": "entry",
      "line": "procreate",         // "procreate" | "lifestyle" — keeps positioning clean
      "craft":   ["portraits", "illustration"],
      "improve": ["skin", "texture", "shading"],
      "level":   ["beginner", "intermediate", "advanced"],
      "style":   ["realistic", "painterly", "textured"],
      "stage":   "texture",        // position in the workflow ladder
      "priority": 92               // editorial weight, breaks ties — NOT a sales claim
    }
  }
}
```

Generated derivative: **`js/finder-index.js`** → `window.DKP_FINDER` (slim projection: slug,
name, price, tier, image, assets, craft/improve/level/style, priority, payhipUrl, url).
Same delivery pattern already proven by `js/search-index.js`, so it inherits the existing
caching, `defer` and `file://` behaviour.

**Future data (Phases 2–5) stays file-based until there is a reason not to:**
`data/reviews.json` (empty until real reviews exist — renders nothing until populated) ·
`data/artists.json` (approved submissions only) · `data/trends/*.json` (Trend Radar output,
private branch) · `reports/weekly-<date>.md` (generated weekly report).

---

## PART 11 — IMPLEMENTATION ORDER

### ✅ PHASE 1 — SALES FOUNDATION (this changeset)
| Step | Item | Why here |
|---|---|---|
| 1.1 | `data/discovery.json` — tier + finder mappings for all 51 products | Everything else reads it |
| 1.2 | `js/analytics.js` + event wiring | Must exist **before** the other changes so their impact is measurable from day one |
| 1.3 | Master Library flagship band (homepage) + upgrade panel (every PDP) | Highest revenue-per-line-of-code change available |
| 1.4 | Brush Finder: `find-my-brushes.html` + `js/finder.js` + nav entry | Solves the #1 conversion problem |
| 1.5 | "What do you create?" craft grid on homepage | Routes intent before the catalog |
| 1.6 | Product hierarchy rendering (tiers on homepage + catalog; Procreate art separated from planners/lifestyle — nothing deleted) | Gives the catalog a spine |
| 1.7 | Email-first freebie funnel + `thank-you.html` | Starts list growth + first-purchase offer |
| 1.8 | PDP selling improvements: licence line above the fold, install steps, `requirements` hygiene filter | Removes concrete objections |
| 1.9 | "Why didn't you buy?" feedback (once/session, dismissible) | Cheapest qualitative signal |
| 1.10 | Deterministic homepage (kill daily rotation) + privacy-policy correction | Stability + compliance |
| 1.11 | Sitemap, README, this document | Discoverability + handover |

### PHASE 2 — CONVERSION (next, after Phase 1 data exists)
Email-provider switch (MailerLite/Brevo) + 5-email sequence · real bundle `bundleContents` for
all 6 bundles · review/testimonial architecture with honest empty states · A/B architecture
(URL-parameter variants, static-only, GA4-scored) · PDP media upgrade: **brush → stroke →
application → finished artwork** galleries · dedicated `faq.html` + `contact.html`.

### PHASE 3 — TRAFFIC
Commercial-intent SEO pages (pencil brushes, texture brushes, Procreate Dreams/animation
brushes, beginners' buying page, bundle comparison page) · Pinterest content engine (a
generator that emits pin concepts + destination URLs per product/article — **never** all to the
homepage) · content-opportunity engine · affiliate architecture (Payhip-native first).

### PHASE 4 — INTELLIGENCE (admin-only, private branch, human-approval gated)
Trend Radar (GitHub Actions cron → Reddit/YouTube/Google Trends via official APIs) · Artist
Problem Database · Product Gap Detector (demand vs `data/products.json`, produces a **DRAFT
proposal**, never publishes) · Trend Score 0–100 · Weekly Growth Report (3 prioritised actions) ·
Procreate Update Intelligence · Sales Intelligence Dashboard.

### PHASE 5 — COMMUNITY
Artist submissions (permission-gated) · Artist Spotlight · Workflow Library · personalised
recommendations from finder history.

---

## PART 12 — TESTING CHECKLIST

### Build integrity
- [ ] `python3 tools/build.py` completes with no traceback
- [ ] A **second** consecutive build produces **zero** content diff apart from dates
      (regression test for the daily-rotation churn, C5/C6)
- [ ] `git status` shows no unexpected deletions; `data/products.json` untouched
- [ ] All 51 product pages, 18 articles, 10 categories, 2 seasons still generated
- [ ] `sitemap.xml` and `sitemap.txt` include `find-my-brushes.html` and `thank-you.html`
- [ ] `js/finder-index.js` contains an entry for every product in `data/discovery.json`
- [ ] No product referenced by the finder is missing from `BY_SLUG` (generator must fail loudly)

### HTML / SEO
- [ ] One `<h1>` per page; heading order unbroken (h1 → h2 → h3)
- [ ] Canonical, OG, Twitter, `Product`/`Offer`, `FAQPage`, `BreadcrumbList` JSON-LD still valid
      (paste into Google's Rich Results Test)
- [ ] New pages have unique titles < 60 chars and meta descriptions < 160 chars
- [ ] No `href="#"`, no dead relative links (crawl check on the local server)
- [ ] `robots.txt` and verification tokens unchanged

### Functionality (desktop + iPad + phone)
- [ ] **Brush Finder:** all 4 questions answerable; every one of the 7 crafts × 8 goals ×
      3 levels × 5 styles produces a non-empty result (560+ combinations — script-verified)
- [ ] Finder works with JS disabled (server-rendered form + grouped catalog fallback visible)
- [ ] Finder result shows product image, description, price, asset count, compatibility, BUY
- [ ] "WANT EVERYTHING?" Master Library block always present in results
- [ ] Portrait answers surface the Masterclass; beginner answers surface a free pack
- [ ] **Upgrade panel** appears on entry/bundle PDPs, never on the flagship itself
- [ ] Every Buy/Get CTA reaches the correct Payhip URL (all 51 verified against `products.json`)
- [ ] Freebie email form: valid address → thank-you page; invalid address → inline error;
      FormSubmit unreachable → graceful native POST fallback
- [ ] Feedback sheet appears once per session, is dismissible, never blocks a CTA, never
      re-appears after dismissal
- [ ] Search overlay (`⌘K`), category filters, gallery + lightbox all still work

### Analytics
- [ ] GA4 DebugView shows `homepage_view`, `product_view`, `outbound_payhip_click`,
      `product_buy_click`, `brush_finder_started`, `brush_finder_completed`,
      `recommendation_clicked`, `upgrade_clicked`, `free_download_click`, `email_signup`,
      `feedback_reason`, `scroll_depth`, `search_query`
- [ ] With `navigator.doNotTrack = 1`, **no** GA4 request is sent
- [ ] With `window.DKP.analytics = false`, nothing fires at all
- [ ] No new cookie appears in DevTools → Application → Cookies from DigiKitPro code
- [ ] No PII in any event payload (grep the event log for `@`)

### Performance (must not regress)
- [ ] Lighthouse mobile Performance ≥ current baseline on `index.html`, `products.html`,
      a product page and `find-my-brushes.html`
- [ ] Total JS added < 30 KB uncompressed; all new scripts `defer`
- [ ] No new render-blocking request; no layout shift from the new homepage sections
      (CLS ≤ current)
- [ ] LCP element on the homepage is unchanged and still `fetchpriority="high"`
- [ ] New images (if any) are WebP with `srcset`, `width`/`height`, `loading="lazy"`

### Compliance / honesty
- [ ] `privacy.html` discloses GA4 and Google Translate accurately
- [ ] Zero fabricated reviews, testimonials, customer counts, star ratings, sales numbers,
      urgency or scarcity anywhere in the diff (`grep` for "left", "only", "sold", "★")
- [ ] No product removed, no price changed, no Payhip URL changed
- [ ] Feedback and newsletter copy states what actually happens

### Deploy
- [ ] Push to the working branch → `Build & deploy site` workflow green
- [ ] Live URL serves the new pages (200, not 404)
- [ ] `sync-payhip.yml` still runs clean against the new generator (dry run)

---

## APPENDIX — What testing found and fixed before this shipped

Phase 1 was verified by executing the real generated artifacts, not by reading
the code. Two defects were caught and fixed; both would have quietly undermined
the whole exercise.

### D1 — The Brush Finder recommended the most expensive bundle for almost every answer

**Symptom.** Run against the first build, three answer sets out of nine returned
*Master Vault Mega Bundle: 1,000+ brushes* ($15) or the *Master Library* ($19)
as the "recommended starting point", and the `brush_finder_completed` event
logged `recommended_id: master-library-2000-brushes, match_score: 100` for a
visitor who had said "illustration / hair / intermediate / stylized".

**Cause.** Whole-catalog libraries legitimately list every craft, every goal,
every level and every style, because they contain everything. Under any additive
relevance scoring they therefore hit the ceiling — 40+30+15+10+5 = 100 — on
**all 1,080** possible answer combinations. A relevance engine with no exclusion
rule is structurally an upsell engine.

**Fix.** Added `"aggregate": true` to the three whole-catalog libraries in
`data/discovery.json` and excluded aggregates from ranking in both the browser
engine (`js/finder.js`) and the Python fallback (`tools/pages_finder.py`). They
are now surfaced only in their own clearly-labelled "Want everything?" slot,
with the price arithmetic shown, plus a "Compare all libraries" link — so
choosing one is a decision made with the numbers visible, not a default.

**Re-verified across all 1,080 combinations:**

| Check | Result |
|---|---|
| Empty result (fallback shown) | **0** |
| Aggregate as primary recommendation | **0** |
| Lifestyle product (planner/travel) as primary | **0** |
| Primary tier spread | entry **1,068** · bundle **12** |
| Distinct products that can be the primary | **26** |

### D2 — Analytics logged a different product from the one the visitor saw

**Symptom.** `brush_finder_completed` reported the raw top-of-list candidate
while the page displayed the specialist pack actually rendered. The owner would
have been optimising against numbers that contradicted the UI.

**Fix.** The event now reports `lastPrimary` — the product actually rendered —
plus `recommended_tier`. Confirmed in the Node run:
`{"craft":"illustration","improve":"hair","level":"intermediate","style":"stylized",
"recommended_id":"hair-hairstyle-stamp-kit","recommended_tier":"entry","match_score":98.8}`.

### D3 — The completion event fired up to 4× per finished quiz

**Cause.** `completedFor` was reset on every answer change, defeating its own
dedupe. **Fix.** Removed; `paint()` already re-fires when the answer key genuinely
changes. **Re-verified:** 3 redundant re-selections of the same answers → 0 extra
events, while a real answer change still fires exactly once.

### Verification actually performed

| Test | Method | Result |
|---|---|---|
| Finder logic, 9 hand-built answer sets | `js/finder.js` executed in Node against a DOM shim and the **real** `js/finder-index.js` | 9/9 render primary + alternates + flagship + specs + "why" + working Payhip CTA; education cross-sell, beginner free pick and the honest animation notice all fire on the right answers |
| Finder logic, all 1,080 combinations | Python mirror of the shipped scoring against the generated index | 0 empty, 0 aggregate/lifestyle primaries |
| Event dedupe + restart + answer editing | Node DOM shim | pass |
| Analytics: normal visit | `js/analytics.js` executed in a Node VM with the `window.DKP.page` context **parsed out of the generated HTML** | `product_view` with correct `product_id`, `tier`, `category`, `price` |
| Analytics: `Do Not Track = 1` | same | 0 gtag calls, `track()` returns `false` |
| Analytics: `#dkp-analytics=off` | same | 0 gtag calls, opt-out persisted to `localStorage` |
| Analytics: build-time kill switch | `DKP_ANALYTICS=false` | module fully inert |
| PII leak | Serialised every event payload and the local log | no `@`, no `mailto`, no identifiers |
| Build determinism | Two consecutive full builds, 108 generated files diffed | **byte-identical** |
| Internal link integrity | All `href`s in all 95 HTML files resolved against the filesystem | **0 broken** |
| Payhip URL integrity | Every Payhip link in the HTML matched against `data/products.json` | 51/51 product pages carry their own real URL; the only extra is `payhip.com/privacy` from the new privacy copy |
| Heading structure | `<h1>` count per page | exactly one on every real page (the two exceptions are search-engine verification token files) |
| Upgrade panel targeting | Grepped all 51 PDPs | present on **37**; correctly absent on the flagship (1), the 4 free packs and the 9 lifestyle products |
| Licence line / install steps | Grepped all 51 PDPs | licence on 51, install steps on 47 (the 4 free packs are excluded deliberately) |
| Generator resilience | `python3 tools/build.py` from a clean tree | completes with no traceback; no untagged-product notice, because all 51 are tagged |

### Still to verify (needs a browser or a live deploy — cannot be done here)

- Lighthouse mobile score before/after on `index.html`, `products.html`, a PDP
  and `find-my-brushes.html` (JS added: 12.7 KB analytics + 19.7 KB finder +
  9.0 KB feedback + 45 KB generated finder index, all `defer`red; CSS +16 KB)
- GA4 **DebugView** confirmation that each event arrives with its parameters
- Real FormSubmit round-trip → redirect to `thank-you.html?lead=…`
- Finder, feedback sheet and card layout on a physical iPad and a small phone
- `sync-payhip.yml` dry run against the new generator
- Google Rich Results Test on the changed product and finder pages

---

## Success metrics (how this work is judged)

**Primary:** orders · revenue · conversion rate
**Secondary:** email subscribers · freebie→email conversion · AOV · repeat purchase rate ·
product-page conversion · organic traffic

All of these are currently **unmeasurable** — which is why step 1.2 (event tracking) is
sequenced before every visible change. After this changeset the owner can answer, for the
first time: *which product pages get traffic and no buy-clicks, which finder answers lead to
purchases, and whether the Master Library band moves AOV.*

**Baseline to record on day 1 (before/after comparison):** GA4 sessions, `product_view` by
product, `outbound_payhip_click` by product, `brush_finder_completed` by answer set,
`email_signup` by source, `feedback_reason` distribution.
