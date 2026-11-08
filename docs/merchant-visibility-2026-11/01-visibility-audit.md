# Phase 1 — Google Merchant Center Visibility Audit (2026-11-08)

## 0. Access & authorisation status

**Not available in this environment** — no Merchant Center or Search Console credentials, no Merchant API, no authorized browser session. Nothing in this document claims product-level impressions, clicks, CTR, disapprovals or indexing. What follows is a **structural audit** (feed + catalog + site + public web + official Google docs). Every account-side cell is marked **OWNER** with the exact export path. If you later authorize API access, this audit regenerates with real numbers.

## 1. What is actually submitted today ([Repo])

`google-merchant-feed.xml` (built 2026-11-08): **44 items** (pro-sketch held = 1), ~140 KB. Catalog = 51 products; excluded-from-feed by policy: 4 free products, `procreate-portrait-masterclass-ebook` ($19, Guides & eBooks), `morocco-7-day-itinerary` ($5).

| Class | Items | Google category | Notes |
|---|---|---|---|
| Procreate brushes/stamps/assets | 31 | 500046 (verified node, `data/google-taxonomy-nodes.json`) | Product-type-first titles (2026-10-29), counts vs record |
| Digital planners / journals | 7 | 8022 | same review process |
| KDP Canva templates | 1 | 8022 | |
| Halloween PNGs | 1 | 500046 | seasonal; eligibility vs MC seasonal handling to confirm |
| **Held** | **1** | — | `pro-sketch-traditional-art-kit` — .rar deliverable; fix = Payhip ZIP re-upload |

Attributes: `identifier_exists=no` + blank GTIN/MPN everywhere — **correct** for own-brand digital goods ([Official] identifier policy: supply identifiers only when assigned; never reuse SKU as GTIN). `condition=new`, `availability=in_stock`, `brand=DigiKitPro`, `price` USD, `link` = PDP, `image_link`/`additional_image_link` present (45/44 items with 4 images except as flagged), `structured_description` carries AI-origin disclosure (`trained_algorithmic_media` on AI-sourced copy) — consistent with Google's generative-AI disclosure guidance and honest. Highlights: 44/44 ≥2; **8 items under the >4-highlight quality bar** (see 03 CSV, P2 rows: dreamy-pastel, digital-sketchbook, premium-texture, undated-planner, mindfulness-planner, wellness-fitness, halloween-pumpkin, professional-hair-brushes). **33/44 sit at the >4 / >5-details bar** (audit register).

## 2. Where your products CAN appear — and the requirements ([Official] answer/13889434, fetched 2026-11-08)

Google free listings show products on **Google Search, Google Images, Google Lens, YouTube, Google Maps / Business Profile products module, Gemini, Shopping tab**. PDP pages are eligible surfaces; **category/policy/other pages are not**. Eligibility requirements (account + feed):

| Requirement | DigiKitPro status | Action |
|---|---|---|
| Free listings enabled (default on new accounts; check Marketing → Marketing methods → Free listings card) | **UNKNOWN** (no MC access) | OWNER: confirm status; ensure Admin access |
| Policies for showing products [Official answer/12073010] | structurally plausible — no physical claims, digital goods, clear "no physical item ships" copy | OWNER: read policy once before next fetch; report flags |
| **Return policy on site** | ✅ `refunds.html` exists; linked from trust bridge on PDPs | ✅ done |
| **Return policy in MC** | UNKNOWN | OWNER: add refunds URL in MC |
| **Shipping settings (mandatory in US + 30 other countries)** [Official] — note: for digital goods this is normally handled as a digital service / zero-cost shipping config | **UNKNOWN** — audit register item E | **OWNER: configure US shipping (digital goods, 0 USD) in MC Settings → Shipping. Without this, US free listings are not eligible.** |
| Feed ↔ site parity (id/title/price/availability match) | ✅ QA-enforced (115 checks incl. price=snapshot vs PDP; `05-landing-evidence.csv` 44/44 PDPs verified for 200/canonical/price-match) | maintain on every rebuild |
| Identifiers | no GTIN/MPN; `identifier_exists=no` | ✅ correct |
| Structured data on PDPs (Product + offers) | ✅ present; validated structurally (qa_seo) | OWNER: Rich Results Test on 5 PDPs for reassurance |
| Countries / languages | English only; US + rest unconfigured | OWNER: confirm target country = US (or add) |

**Category fit caveat (F):** `500046`/`8022` are the closest available nodes for digital art assets; Google "accepts overrides only in 3 cases" for Shopping ads categories — for free listings accuracy matters, but the MC "Needs attention" tab is the arbiter; OWNER: confirm no field-requirement warning; keep or revert once seen.

## 3. "Which products get zero impressions" — the honest answer

Cannot be known offline — Google reports **per-product** impressions only in MC (Reports → Products / All products tab, or Products → All products → download). Pre-registered expectations, to be tested against your export (14-day and 28-day windows; refresh after any eligibility fix):

| Probe | Prediction (tune against export) | Why |
|---|---|---|
| Zero-impression likely | 4 low-search-volume seasonal/planner SKUs (halloween-pumpkin-bundle, wellness journals, adhd-planner-2026, undated-planner-dark-mode) | Term volume tiny or audience mismatch (US planner market crowded) |
| Low-impression likely | mega-bundle-650 / library-2000 / vault-1000 (names carry generic mega words but compete with marketplace mega-listings) | Head term is marketplace land |
| Most promising | portrait-skin-brushes, portrait-mastery-kit, essential-line-art, ultimate-bundle, liner-marker-studio, tattoo-artist-studio-kit-200 | Precise brushes; site has guides + before/after to match |
| Unknown | everything else | No account data exists |

Decision rule: **any item with <10 impressions over 28 days AND no eligibility flag** → demote from "optimize" to "leave; revisit after content lands" or consider deliberate exclusion from the feed to cut noise (your call; not done here).

## 4. Feed quality gates (repo-verifiable, all PASS 2026-11-08)

44/44 categories reviewed nodes · titles product-type-first ≤ ~76 chars · price=USD · `in_stock` · `new` · single description field (+structured AI disclosure) · deterministic rebuild · indexnow=current · 5 PDP-linked Q&A blocks · alt text enforced.

## 5. OWNER export checklist (≤60 min; closes this phase)

1. MC → Marketing → Marketing methods → capture "Free listings" card status (screenshot)
2. MC → Shipping & returns → confirm US shipping configured for digital goods (or add; add refunds URL)
3. MC → Products → All products → **download CSV** (all 44): columns impressions, clicks, CTR, approval status, destination eligibility (Free listings column), last-fetch
4. MC → Products → Needs attention → screenshot every warning/disapproval with item IDs
5. GSC → Performance → last 16 months → export pages+queries CSV; Indexing → Pages → export
6. File exports in `docs/growth-strategy-2026-11/baseline-data/` (aggregate CSVs OK to commit; keep customer data out)
7. Bring the four headline numbers to `08-measurement-dashboard.md`

## 6. Bottom line

Structurally the feed is clean, honest and correctly identified (no fabricated GTINs, no misrepresented digital status, price parity enforced). The two things that can zero-out visibility are **US shipping settings** and **Free listings account status** — both OWNER-verifiable in minutes, both currently unproven. Until the export lands, every impression claim in this pack is inference.
