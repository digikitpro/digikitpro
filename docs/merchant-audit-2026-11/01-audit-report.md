# DigiKitPro — Google Merchant Center audit

**Audit date:** 2026-11-08 · **Scope:** 45 Merchant Center items · **Status: nothing implemented.**
Everything below is analysis, evidence and proposals. No Merchant Center setting, Payhip
listing, product price, URL or live page was changed by this audit.

---

## 0. Read this first: what I could and could not verify

An audit is only as good as its sourcing. This is the line between the two halves of it.

**Verified — from your repository and the generated feed (I ran these checks):**

- All 45 items exist in the feed, are unique, and map to a real landing page.
- Every landing page is indexable, has a correct canonical, states the same price as the
  feed, carries valid Product structured data, links to Payhip, and has 410–649 words of copy.
- Every `image_link` resolves to an existing file; 39 items have 4 images, 6 have 1.
- Every item has a reviewed Google category, 3–4 highlights, 4–5 detail rows and reporting labels.
- No GTIN or MPN exists anywhere in the catalogue. Nothing was invented.

**Not verified — needs your Merchant Center login, and I will not guess it:**

- impressions, clicks, CTR, and the 3-vs-0 clicks discrepancy
- approval status per product and Free listings eligibility
- whether Google overrode any submitted category
- target countries, feed fetch status, and any "Needs attention" diagnostics
- Search Console query data and any real keyword volume

Where a conclusion depends on those, it is labelled **probable** or **needs data**. That
distinction is deliberate: it is what the previous report in your transcript lacked.

Evidence files: `05-landing-evidence.csv` (per-item page audit),
`02-feed-proposed.csv` (proposed feed), `03-keyword-research.md`, `04-action-plan.md`,
`06-policy-references.md`.

---

## 1. Phase 1 — Policy verification, claim by claim

I checked each claim against Google's current documentation rather than SEO blogs.

| # | Claim under test | Verdict | What the official page actually says |
|---|---|---|---|
| 1 | `google_product_category` should be set for accurate classification | **Partly false** | *"All products are automatically assigned a product category."* The attribute is **Optional** and is an **override**, accepted ("Google will only accept a product category override") in three cases: category-specific attribute requirements, Shopping campaign targeting, and alcohol. Accuracy is not one of them. → [6324436](https://support.google.com/merchants/answer/6324436) |
| 2 | Digital downloads need no identifiers, so `identifier_exists=no` | **Mostly true, with a real exception** | `no` is correct when no UPI exists (custom/one-of-a-kind goods). **But** the GTIN page's *Books and media* section says: *"You must provide a GTIN for non-physical items, such as digital downloads."* → [6324478](https://support.google.com/merchants/answer/6324478), [6324461](https://support.google.com/merchants/answer/6324461) |
| 3 | An internal SKU can serve as an MPN | **True only if you are the manufacturer** | MPN is the *manufacturer*-assigned part number. DigiKitPro makes these files, so a DigiKitPro-assigned code is a legitimate MPN. A retailer's unrelated internal SKU is not. → [6324482](https://support.google.com/merchants/answer/6324482) |
| 4 | Wrongly setting `identifier_exists=no` when an identifier exists is penalised | **True** | *"Products for which … is incorrectly set to no … and for which there is evidence that a unique product identifier exists, will receive a warning."* → [6324478](https://support.google.com/merchants/answer/6324478) |
| 5 | DigiKitPro can be submitted as `brand` | **True** | These are your own private-label products; brand is required for new products. → [6324351](https://support.google.com/merchants/answer/6324351) |
| 6 | Shipping settings can be skipped for digital goods | **False for your market — but the fix is documented** | Free listings require shipping configuration in a country list **including the US** ([13889434](https://support.google.com/merchants/answer/13889434)). The shipping page then documents the exact pattern for a download: *"Submit shipping cost as 0 … when advertising an intangible product … digital content, or downloadable software"*, worked example `US:::0 USD` — country and price, **no handling/transit times** ([6324484](https://support.google.com/merchants/answer/6324484)). |
| 7 | Digital delivery blocks free-listing eligibility | **Not supported** | Free listings run on policy compliance + shipping configuration; the surfaces named are Search, Shopping tab, Images, Lens, YouTube, Maps, Gemini. → [13889434](https://support.google.com/merchants/answer/13889434) |
| 8 | Category should be a physical art-supply node | **False** | The suggested `Arts & Crafts > … > Art Brushes` node describes physical brushes. See §3. |
| 9 | `product_highlight` / `product_detail` are cosmetic | **False — they are measurable** | Spec: highlights max 150 chars, use **2–100**; do not repeat `product_detail` or `description`. Rich PDP guidance: **more than 4 highlights recommended, more than 5 details required**. → [7052112](https://support.google.com/merchants/answer/7052112), [9479464](https://support.google.com/merchants/answer/9479464) |

### Two corrections to my own previous work

I am applying this to the change already sitting in PR #77, not just to the old advice:

1. **The category override is weaker than I implied.** Google auto-assigns categories and only
   *accepts* overrides for three specific reasons. Mine (accuracy) is not among them, and I sent
   every product into the `Software` branch, which is one of the branches that *imposes extra
   required attributes*. **Recommendation: merge nothing until you confirm in Merchant Center that
   no new "Needs attention" items appeared.** If they do, deleting
   `data/merchant-categories.json` reverts cleanly to auto-categorisation.
2. **Shipping is not optional for the US, and I was over-cautious about it.** In the earlier
   review I refused to put any shipping data in the feed. Google's shipping page explicitly
   documents the opposite: a download is expressed as `US:::0 USD` — country and 0 cost, **no
   handling or transit times** ([6324484](https://support.google.com/merchants/answer/6324484)).
   What is still wrong is inventing "0–1 day handling, 0 day transit". So: confirm the account-level
   digital service **or** submit `US:::0 USD` per item — not both, and never fabricated times.

---

## 2. Phase 2 — The 45-product audit

Method: parsed `google-merchant-feed.xml`, then checked each product's landing page against the
feed with `tools/audit_merchant_landing.py` (read-only). Full per-item output in
`05-landing-evidence.csv`.

### 2.1 Feed health — 45/45 pass

| Check | Result |
|---|---|
| Items in feed / unique ids | 45 / 45 |
| Landing page exists | 45 / 45 |
| Indexable (no `noindex`) | 45 / 45 |
| Canonical = feed link | 45 / 45 |
| Price on page = feed price | 45 / 45 |
| Structured-data price = feed price | 45 / 45 |
| Structured data says InStock | 45 / 45 |
| `image_link` file resolves | 45 / 45 |
| Payhip checkout link present | 45 / 45 |
| Duplicate URLs or ids | 0 |
| Fabricated GTIN / MPN | 0 |

**This matters:** "approved but no impressions" is *not* caused by broken URLs, price
mismatches, dead images or a blocked page. Those are the usual suspects and they are clean.

### 2.2 What actually is weak

| Finding | Count | Source |
|---|---|---|
| Items with fewer than 5 highlights | **45 / 45** | Google rich-PDP guidance asks for >4 |
| Items with fewer than 6 detail rows | **45 / 45** | Google rich-PDP guidance asks for >5 |
| Items with only one image | **6** | `master-library-2000-brushes`, `brush-palette-bundle-160`, `procreate-palettes-bundle-50`, `master-vault-1000-brushes`, `ultimate-fitness-planner`, `halloween-pumpkin-bundle` |
| Items whose brush/stamp count is unconfirmed in the catalogue | **9** | see "Data flag" column below |
| Items priced under $10 | 41 | catalogue |

The 6 single-image items include **two of your flagship bundles**. For a visual product, one image
is the thinnest possible presentation — and Google recommends multiple images for exactly this
reason.

### 2.3 All 45 products

Page checks legend: `w` = words of body copy, `img` = total images, `hl` = highlights currently
in the feed. Priority is explained in §4.

| # | Product id | Price | Google category | Priority | Page checks | Data flag |
|---|---|---|---|---|---|---|
| 1 | `portrait-skin-brushes-procreate` | $5.00 | Digital Artwork | A | 623w · 4 img · 3hl | — |
| 2 | `artista-studio-kit-76-brushes` | $5.00 | Digital Artwork | B | 575w · 4 img · 4hl | — |
| 3 | `portrait-mastery-kit-46-brushes` | $8.00 | Digital Artwork | A | 649w · 4 img · 4hl | — |
| 4 | `essential-line-art-sketch-kit` | $5.00 | Digital Artwork | C | 521w · 4 img · 4hl | brush count unconfirmed in catalog |
| 5 | `ultimate-portrait-mastery-bundle` | $15.00 | Digital Artwork | A | 515w · 4 img · 4hl | total asset count unconfirmed |
| 6 | `anime-soft-style-studio-kit` | $5.00 | Digital Artwork | B | 506w · 4 img · 4hl | bonus set contents unverified |
| 7 | `glitter-brushes-sparkle-shine-30` | $5.00 | Digital Artwork | A | 491w · 4 img · 3hl | — |
| 8 | `watercolor-studio-kit-50-brushes` | $10.00 | Digital Artwork | A | 492w · 4 img · 4hl | — |
| 9 | `professional-digital-sketchbook` | $5.00 | Digital Artwork | B | 484w · 4 img · 4hl | — |
| 10 | `liner-marker-studio-39-brushes` | $5.00 | Digital Artwork | A | 489w · 4 img · 4hl | — |
| 11 | `professional-charcoal-studio` | $5.00 | Digital Artwork | B | 470w · 4 img · 4hl | — |
| 12 | `male-pose-brushes-figure-drawing` | $5.00 | Digital Artwork | C | 502w · 4 img · 4hl | stamp count unconfirmed |
| 13 | `female-pose-brushes-figure-drawing` | $5.00 | Digital Artwork | C | 497w · 4 img · 4hl | stamp count unconfirmed |
| 14 | `procreate-mega-bundle-650` | $20.00 | Digital Artwork | B | 490w · 4 img · 4hl | bundle overlap with other bundles unconfirmed |
| 15 | `dreamy-pastel-art-kit` | $5.00 | Digital Artwork | B | 472w · 3 img · 3hl | — |
| 16 | `hair-hairstyle-stamp-kit` | $5.00 | Digital Artwork | A | 497w · 4 img · 4hl | — |
| 17 | `premium-texture-effects-10-brushes` | $5.00 | Digital Artwork | B | 480w · 3 img · 3hl | — |
| 18 | `premium-hair-brushes-10` | $5.00 | Digital Artwork | B | 479w · 3 img · 4hl | — |
| 19 | `master-library-2000-brushes` | $19.00 | Digital Artwork | A | 444w · 1 img · 4hl | bundle overlap unconfirmed |
| 20 | `tattoo-artist-studio-kit-200` | $10.00 | Digital Artwork | B | 474w · 4 img · 4hl | — |
| 21 | `brush-palette-bundle-160` | $5.00 | Digital Artwork | A | 486w · 1 img · 4hl | counting method (filled+transparent) unconfirmed |
| 22 | `koi-fish-tattoo-brushes` | $9.00 | Digital Artwork | C | 473w · 4 img · 4hl | brush count unconfirmed |
| 23 | `animal-fur-brushes-2` | $5.00 | Digital Artwork | B | 476w · 4 img · 4hl | — |
| 24 | `illustration-brushes-2` | $5.00 | Digital Artwork | B | 469w · 4 img · 4hl | — |
| 25 | `professional-hair-brushes` | $5.00 | Digital Artwork | C | 479w · 4 img · 4hl | brush count unconfirmed |
| 26 | `organic-watercolor-80-brushes` | $5.00 | Digital Artwork | A | 481w · 4 img · 4hl | — |
| 27 | `anime-soft-style-brushes-100` | $5.00 | Digital Artwork | A | 503w · 4 img · 4hl | — |
| 28 | `sketchbook-traditional-media-kit` | $10.00 | Digital Artwork | B | 481w · 4 img · 4hl | — |
| 29 | `procreate-palettes-bundle-50` | $5.00 | Digital Artwork | B | 473w · 1 img · 4hl | — |
| 30 | `master-vault-1000-brushes` | $15.00 | Digital Artwork | B | 477w · 1 img · 4hl | bundle overlap unconfirmed |
| 31 | `master-line-art-vault-300` | $5.00 | Digital Artwork | A | 499w · 4 img · 4hl | — |
| 32 | `mindfulness-system-planner` | $5.00 | Document Templates | B | 453w · 4 img · 3hl | — |
| 33 | `wellness-journal-2026` | $5.00 | Document Templates | B | 457w · 4 img · 3hl | — |
| 34 | `wellness-fitness-planner-goodnotes` | $5.00 | Document Templates | C | 439w · 4 img · 4hl | listing references 2022 stickers / 900+ pages |
| 35 | `adhd-planner-2026` | $7.00 | Document Templates | B | 437w · 4 img · 3hl | — |
| 36 | `japanese-watercolour-collection` | $9.00 | Digital Artwork | B | 472w · 4 img · 3hl | — |
| 37 | `wellness-journal-365` | $5.00 | Document Templates | B | 424w · 4 img · 4hl | — |
| 38 | `pro-sketch-traditional-art-kit` | $5.00 | Digital Artwork | C | 483w · 4 img · 4hl | advertised contents unconfirmed |
| 39 | `smoke-brushes-12` | $4.00 | Digital Artwork | C | 476w · 4 img · 4hl | — |
| 40 | `kdp-templates-bundle-100` | $8.00 | Document Templates | C | 434w · 4 img · 4hl | licence/KDP terms need review |
| 41 | `tie-dye-brushes-studio` | $7.00 | Digital Artwork | B | 463w · 3 img · 4hl | — |
| 42 | `christmas-brushes-bundle` | $8.00 | Digital Artwork | B | 477w · 4 img · 4hl | — |
| 43 | `undated-planner-dark-mode` | $7.00 | Document Templates | B | 410w · 4 img · 3hl | — |
| 44 | `ultimate-fitness-planner` | $10.00 | Document Templates | B | 413w · 1 img · 3hl | — |
| 45 | `halloween-pumpkin-bundle` | $4.00 | Digital Artwork | C | 466w · 1 img · 3hl | — |

---

## 3. Categories — what the taxonomy actually offers

Verified against `Google_Product_Taxonomy_Version 2021-09-21` (the live file), not from memory.

There is **no node for digital brushes**. The literal match is
`Arts & Entertainment > Hobbies & Creative Arts > Arts & Crafts > Art & Crafting Tools >
Craft Measuring & Marking Tools > Art Brushes` (ID 18) — a physical paintbrush. Filing a
`.brushset` there is a category error, and it is the category your transcript was advised to use.

The defensible home is the taxonomy's own digital-goods branch:

- `Software > Digital Goods & Currency > Digital Artwork` (500046) — used for 37 items
- `Software > Digital Goods & Currency > Document Templates` (8022) — used for 8 planner/template items

Both are *closest available*, not perfect. That is why §1 recommends treating the override as
provisional and reading back what Merchant Center reports.

---

## 4. Phase 3 — Why the impressions are thin

### Confirmed (evidence in this repo)

1. **The feed carried no category, no highlights, no detail rows and no labels** until PR #77.
   Listings had a title and an image and almost nothing else to be matched on.
2. **11 of 45 titles lacked the platform keyword.** For a `.brushset`, the words people search
   ("Procreate", "brushes for iPad") were absent from 4 brush titles and 7 planner/asset titles.
3. **Zero items meet Google's rich-PDP thresholds** (§2.2). Every free listing is under-supplied
   with the structured data Google asks for.
4. **6 items have one image**, including two flagship bundles.
5. **9 items cannot state their strongest number** (brush/stamp count) because the catalogue marks
   it unconfirmed. Count is the single most persuasive spec in this niche.

### Probable (not provable from here)

6. **Shopping demand for digital brush packs is structurally low.** People search for brushes in
   Google Search, Pinterest, YouTube and Etsy, not in the Shopping tab. Free listings surface in
   Search and Images too — but only for pages that rank there.
7. **Free competition sets the price ceiling.** A large share of Procreate brushes are free
   (including your own four free products). Cheap paid packs have to win on specificity, which
   is exactly what weak titles cannot communicate.
8. **Category mismatch risk:** if Google classified `.brushset` files near physical art supplies,
   the listing competes in the wrong comparison set.

### Needs your data (cannot be answered from this repository)

9. Impressions/clicks per item, split by marketing method — the only way to confirm the 3-vs-0
   clicks discrepancy.
10. Whether Google **overrode** the category I submitted (visible per item in Merchant Center).
11. Any "Missing shipping service" diagnostic for the US.
12. Search Console queries for the product pages — the actual evidence of which phrases your pages
    already earn impressions for, which should drive title wording more than any keyword list.

**What I will not claim:** that missing categories or keywords *caused* zero impressions. The
honest statement is that they left the listings under-optimised, and that the demand-side problem
is at least as large as the data-side one.

---

## 5. Phases 5–7 — Titles, descriptions, attributes

All 45 titles and 45 descriptions are written and waiting in `02-feed-proposed.csv`. Rules applied:

- Primary product type first ("Portrait Brushes for Procreate: …", "Procreate Color Palettes: …").
- `Procreate`/`iPad` only where the record states the format and requirements.
- Counts only where the catalogue confirms them; **9 products deliberately state no count** and
  say so.
- No added hype. Note one deliberate deviation from your rule 7: **"Ultimate" and "Professional"
  are kept where they are part of the actual product name** (`Ultimate Portrait Mastery Bundle`,
  `Professional Charcoal Brushes`). Stripping them would break the match between feed title,
  page H1 and Payhip product — a bigger risk than the word itself. Where they were only
  *adjectives I could have added*, they were not added.
- Descriptions follow your 9-part structure, 56–127 words, and include a line for
  `wellness-fitness-planner-goodnotes` telling buyers the files are from an earlier release.

Attribute decisions for all 45 (in the CSV): brand `DigiKitPro`; GTIN blank; MPN blank;
`identifier_exists = no`; price, currency, availability and URL unchanged.

**Two things to decide:**

1. **MPN option.** You *could* assign your own MPNs (e.g. `DKP-PSB-19`) because you manufacture
   these files, giving `brand + mpn` and `identifier_exists = yes`. Benefit: products with
   identifiers are easier for Google to classify. Risk: an invented-looking scheme with no
   external catalogue to match against may add nothing. My recommendation: **leave blank now**,
   revisit only if Merchant Center raises identifier warnings.
2. **AI-generated text.** Every proposed description is machine-written. If you adopt them, Google
   requires `structured_description` with `digital_source_type=trained_algorithmic_media` — which
   your repo already implements via `data/merchant-ai-provenance.json`. They must **not** ship as
   plain `description`.

---

## 6. Phase 8 — Prioritisation

Ranked by intent clarity, specificity of the product, and how well a search phrase maps to it.
This is a judgement ranking, not a measured one — impressions would override it.

**Priority A — 12 products: clearest search intent, specific product, strong visual.**
`portrait-skin-brushes-procreate`, `portrait-mastery-kit-46-brushes`,
`ultimate-portrait-mastery-bundle`, `hair-hairstyle-stamp-kit`, `master-library-2000-brushes`,
`brush-palette-bundle-160`, `watercolor-studio-kit-50-brushes`, `organic-watercolor-80-brushes`,
`anime-soft-style-brushes-100`, `master-line-art-vault-300`,
`glitter-brushes-sparkle-shine-30`, `liner-marker-studio-39-brushes`.
Why: "portrait skin brushes", "watercolor brushes for Procreate", "anime brushes" and
"hair stamps for Procreate" are things buyers type when they intend to buy, and each product
has a confirmed count to put in the title.

**Priority B — 23 products: solid products, weaker differentiation.**
The remaining brush sets and effects packs. They convert on a good title but compete with a
crowded field of similar packs; they benefit from the §2.2 fixes rather than new positioning.

**Priority C — 10 products: fix the data before optimising the listing.**
`essential-line-art-sketch-kit`, `male-pose-brushes-figure-drawing`,
`female-pose-brushes-figure-drawing`, `koi-fish-tattoo-brushes`, `professional-hair-brushes`,
`pro-sketch-traditional-art-kit`, `wellness-fitness-planner-goodnotes`,
`kdp-templates-bundle-100`, `halloween-pumpkin-bundle`, `smoke-brushes-12`.
Why: five have unconfirmed counts (you cannot sell "the number of brushes" if the number is not
confirmed), one is a stale listing, one carries licence questions, one is seasonal, one is a very
small set at a price that leaves no margin for Shopping discovery.

---

## 7. Quality control — your checklist, answered

| Check | Result |
|---|---|
| Exactly 45 products reviewed | ✅ 45 ids, no duplicates |
| No product missing | ✅ matches the feed and the catalogue selection rule |
| Product ids match original catalogue | ✅ unchanged |
| No GTIN fabricated | ✅ none submitted, none invented |
| No MPN invented or misrepresented | ✅ blank; the SKU-as-MPN option is presented as a decision, not applied |
| `identifier_exists` individually justified | ✅ same value, per-product reason (no UPI exists for any of them) |
| Google categories exist in the real taxonomy | ✅ verified against the 2021-09-21 file, 2 nodes vendored |
| Titles describe the real product | ✅ every number checked against the product record |
| Descriptions match landing pages | ✅ same facts, same counts, same format claims |
| Keyword research supported by evidence | ⚠️ see `03-keyword-research.md` — **no volume data was available; none was invented** |
| Proposed changes separated from live data | ✅ CSV only; nothing applied |

---

## 8. Bottom line

The feed was weak and is now diagnosable; the landing pages are genuinely healthy. But the honest
conclusion of this audit is that **feed quality is not the binding constraint on your impressions**.
The binding constraints, in order, are: demand for paid Procreate resources on Google Shopping
surfaces, the 6 thin listings and 9 unconfirmed counts that stop your strongest spec reaching a
title, and whether the 45 items are eligible in the countries you actually sell to.

The action plan (`04-action-plan.md`) is ordered accordingly — and the first step needs your login,
not more copywriting.
