# Google Merchant feed — audit and optimisation (2026-11-08)

Scope: the `google-merchant-feed.xml` source that Merchant Center fetches daily
(`PRODUCTS SOURCE 1`, per your account report), the data behind it, and what a
Merchant Center assistant can and cannot do with it.

I changed no prices, URLs, product ids, availability or product pages. Everything
below is either a feed field, a reviewed data file, or a QA guard.

---

## 1. Before you send the assistant anything else: it is not connected to your account

That transcript contains statements no Merchant Center integration would make:

| Claim in the transcript | What the evidence shows |
|---|---|
| "Diagnostic check confirms your account is healthy… 0 policy warnings" | Not verifiable from outside. Nothing in this repo reads your Merchant Center account. |
| "I initiated a fresh data fetch… Confirm to proceed" | Fetches are scheduled by Google on the source URL. An assistant can't queue one, and "confirming" changed nothing. |
| "Your products received 0 clicks… insufficient impressions" **and** earlier "3 clicks" for the same 28 days | Contradictory for the same view. Your dashboard is the authority; the report is generated text. |
| "Availability: Unknown" for every product | Your feed sends `<g:availability>in_stock</g:availability>` on all 45 items (verified below). "Unknown" describes the assistant's knowledge, not your data. |
| "Set attribute rules / apply bulk changes in Data sources" | Those are UI steps **you** perform. It cannot click them, and its suggested rules were wrong for your catalogue anyway (see §5). |

Practical consequence: **optimise the source feed, not the assistant's advice.**
Merchant Center re-fetches `https://digikitpro.shop/google-merchant-feed.xml`
daily, so a feed change here reaches the account without any manual step.

---

## 2. Why 45 approved products can still earn almost no impressions

Approval means "no policy violation". It says nothing about whether Google can
match a listing to a query. Four gaps in the old feed explain the weak matching:

| Field | Before | After | Why it matters |
|---|---|---|---|
| `google_product_category` | 0 / 45 | 45 / 45 | Optional field, but without it Google classifies a `.brushset` download itself — and the physical art-brush nodes are a plausible (wrong) landing spot. |
| `product_highlight` | 0 / 45 | 45 / 45 (3–4 each) | Free-listing bullets. A title alone carries very little surface area. |
| `product_detail` | 0 / 45 | 45 / 45 (4–5 rows each) | Format, contents, file size, delivery, requirements — the attributes shoppers filter and compare on. |
| `custom_label_0..3` | 0 / 45 | 45 / 45 | Your only way to read performance by product class, price band or priority cluster in Merchant Center reports. |
| `title` | 45 plain names | 20 keyword-complete, 25 kept | See §4. |
| `product_type` | `DigiKitPro > <internal category>` | `DigiKitPro > <class> > <category>` | Gives Google a grouping it can use for related queries. |

The feed file grew from 55 KB to 119 KB — all of it product data, no markup padding.

Approval also does not create demand. 45 brush packs at $4–$20 sit in a niche
where **Google Shopping free listings are a weak surface**: shoppers rarely open
Shopping to browse brush sets. Your realistic organic upside is Search and
Images, where your landing pages already have hand-written H1s, titles and
image sitemaps. Merchant Center should be treated as one supporting channel,
which is exactly what your own note concluded.

---

## 3. Category: what I set, and the judgement call inside it

Google's 2021-09-21 taxonomy has **no node for digital brushes**. The nearest
literal match is `Arts & Entertainment > Hobbies & Creative Arts > Arts & Crafts >
Art & Crafting Tools > Craft Measuring & Marking Tools > Art Brushes` — a
**physical** paintbrush. That is the category the earlier transcript recommended,
and using it would place downloadable `.brushset` files in a hardware-style
browse path, which is worse than no category at all.

What I used instead, from the taxonomy's own digital-goods branch:

| Your product class | Google category | Count |
|---|---|---|
| Procreate brushes, stamps, kits, bundles | `Software > Digital Goods & Currency > Digital Artwork` (`500046`) | 34 |
| Procreate `.swatches` palettes | `Software > Digital Goods & Currency > Digital Artwork` (`500046`) | 1 |
| PNG illustration / pattern packs | `Software > Digital Goods & Currency > Digital Artwork` (`500046`) | 2 |
| Hyperlinked PDF planners and journals | `Software > Digital Goods & Currency > Document Templates` (`8022`) | 7 |
| Editable Canva templates | `Software > Digital Goods & Currency > Document Templates` (`8022`) | 1 |

Every id and path is verified against the official taxonomy file, and only those
two nodes are vendored into `data/google-taxonomy-nodes.json` so QA can check the
feed offline forever.

**The honest caveat:** `Digital Artwork` is the closest available node, not a
perfect one, for brush *tools*. `Document Templates` is the closest node for a
planner you write in. Both are defensible (they are downloadable digital goods,
which is what that branch is for), but after the next fetch you should open one
brush product and one planner in Merchant Center and read back the category and
any "incorrect category" note. If Google disagrees, the fix is one line in
`data/merchant-categories.json` — not a bulk rule.

---

## 4. Titles: 20 changed, 25 deliberately left alone

The rule I applied: **add an attribute only if the product's own record already
states it**, and verify every number against that record. 25 titles were already
complete, and rewriting them would have been churn, not optimisation.

Typical fixes:
- `Professional Liner & Marker Studio: 39 High-Fidelity Brushes` → adds **Procreate** (the format and requirements both state it).
- `Animal Fur 2: 35 Fur, Hair & Feather Brushes` → adds **Procreate**.
- `Digital Wellness Journal: 365 Hyperlinked Pages, Dark Mode` → `365-Page Digital Wellness Journal: Hyperlinked PDF, Dark Mode` (format is stated; I did **not** add "for GoodNotes" even though the requirement names it, because the requirement also allows other apps).
- `Halloween Spooky Pumpkin Bundle: 20 PNGs` → adds **300 DPI**, which the record states.

No promotional wording, no invented compatibility, no invented file formats, and
no title over 150 characters. A QA test now re-checks every number in every feed
title against the product record, so a future edit cannot slip an unverified
count in.

| Product | Was | Now | Reason |
|---|---|---|---|
| `portrait-skin-brushes-procreate` | Portrait Skin Brushes for Procreate | **19 Portrait Skin Texture Brushes for Procreate** | Adds the verified brush count from technical contents; 'skin texture' is the product's category. |
| `portrait-mastery-kit-46-brushes` | Portrait Mastery Kit: 46 Procreate Brushes | **Portrait Mastery Kit: 46 Procreate Brushes + 4 Paper Textures** | Adds the four paper textures listed in technical contents. |
| `ultimate-portrait-mastery-bundle` | Ultimate Portrait Mastery Bundle: 4 Procreate Kits | **Ultimate Portrait Mastery Bundle: 4 Procreate Brush Kits** | States that the four kits are brush kits, which every included item confirms. |
| `liner-marker-studio-39-brushes` | Professional Liner & Marker Studio: 39 High-Fidelity Brushes | **Liner & Marker Studio: 39 High-Fidelity Procreate Brushes** | Adds 'Procreate', which the format and requirements both state. |
| `hair-hairstyle-stamp-kit` | Professional Hair & Hairstyle Stamp Kit for Procreate | **Professional Hair & Hairstyle Stamp Kit for Procreate: 160 Stamps** | Adds the verified 160-stamp count from technical contents. |
| `animal-fur-brushes-2` | Animal Fur 2: 35 Fur, Hair & Feather Brushes | **Animal Fur 2: 35 Procreate Brushes for Fur, Hair & Feathers** | Adds 'Procreate' from the .brushset format and requirements. |
| `illustration-brushes-2` | Illustration Brushes 2 for Procreate | **Illustration Brushes 2 for Procreate: 15 Textures + 5 Palettes** | Adds the verified contents (15 texture brushes + 5 palettes). |
| `anime-soft-style-brushes-100` | 100+ Anime Soft Style Brushes: Watercolor, Shading & Line Art | **100+ Anime Soft-Style Procreate Brushes: Watercolor, Shading & Line Art** | Adds 'Procreate' from the .brushset format and requirements. |
| `procreate-palettes-bundle-50` | Procreate Palettes Bundle: 50 Sets × 30 Swatches | **Procreate Color Palettes Bundle: 50 Sets, 1,500 Swatches** | Swaps '×' for a readable swatch total already stated in technical contents. |
| `master-line-art-vault-300` | Master Line-Art Vault: 300+ Fine Line Brushes | **Master Line-Art Vault: 300+ Fine Line Procreate Brushes** | Adds 'Procreate' from the .brushset format and requirements. |
| `mindfulness-system-planner` | 10-Minute Daily Mindfulness System: 57-Page Planner | **10-Minute Daily Mindfulness Planner: 57-Page Hyperlinked PDF** | Adds the verified format (hyperlinked PDF) and drops the vague 'System'. |
| `wellness-journal-2026` | 2026 Digital Wellness Journal | **2026 Digital Wellness Journal: Hyperlinked PDF** | Adds the verified format so the listing reads as a digital download. |
| `adhd-planner-2026` | Digital 2026 ADHD Balanced Mind Planner & Wellness Journal | **2026 ADHD Balanced Mind Planner & Wellness Journal: 55-Page PDF** | Adds the verified page count and PDF format. |
| `japanese-watercolour-collection` | Japanese Watercolour Collection: 43 Illustrations + Patterns | **Japanese Watercolour Collection: 43 Illustrations + PNG Patterns** | Adds the verified PNG format for image-search matching. |
| `wellness-journal-365` | Digital Wellness Journal: 365 Hyperlinked Pages, Dark Mode | **365-Page Digital Wellness Journal: Hyperlinked PDF, Dark Mode** | Leads with the page count and states the verified PDF format. |
| `tie-dye-brushes-studio` | Tie Dye Brushes Studio for Procreate | **Tie-Dye Brushes Studio for Procreate: 21 Brushes & Stamps** | Adds the verified 21-item count. |
| `christmas-brushes-bundle` | Christmas Procreate Brushes Bundle | **Christmas Procreate Brushes & Stamps Bundle: 173 Brushes + 44 Washi Tapes** | Adds the verified counts from technical contents. |
| `undated-planner-dark-mode` | Undated Digital Planner: Dark Mode | **Undated Digital Planner: Dark Mode, Hyperlinked PDF + 1,000 Stickers** | Adds verified format and the 1,000-sticker contents. |
| `ultimate-fitness-planner` | Ultimate Fitness Planner for Peak Performance | **Ultimate Fitness Planner for Peak Performance: Digital PDF** | Adds the verified PDF format. |
| `halloween-pumpkin-bundle` | Halloween Spooky Pumpkin Bundle: 20 PNGs | **Halloween Pumpkin Bundle: 20 PNG Illustrations at 300 DPI** | Adds the verified 300 DPI spec and that they are illustrations. |

---

## 5. Identifier and shipping settings — corrected, not bulk-applied

**`identifier_exists`**: your products genuinely have no GTIN, no MPN and no
manufacturer-assigned part number. `DigiKitPro` is a real brand, but brand alone
does not make `identifier_exists = yes`. So `no` on all 45 is the correct value,
and the builder derives it (`yes` only if a GTIN or brand+MPN exists) rather than
hard-coding it. The earlier advice "set identifier_exists = no for all items via
an attribute rule" reaches the right answer for the wrong reason and would keep
being wrong the day you do have an identifier. **Do not** label your internal
slug as an MPN — that is what Google means by inventing an identifier.

**Shipping**: I added no shipping data to the feed. A downloadable file has no
carrier, no transit time and no handling period, and inventing "0–1 business
days" would be exactly the misleading data you warned about. Your account already
has a digital shipping service per the transcript; if Merchant Center ever flags
a missing service for the US, confirm that service covers these items — do not
create a second one with fabricated times. Note that `shipping` in the feed is a
per-item override, not a requirement for a digital source.

**Two untouched positions that are correct as they stand:**
- The 4 free downloads stay out of this source (a $0 offer is a different
  eligibility question than a paid one), and the 2 eBooks stay out because
  Google excludes eBooks from Shopping. Both keep their landing pages and
  Payhip links; nothing was deleted.
- The PDF travel guide (`morocco-7-day-itinerary`) stays out for the same review
  reason it was held out originally.

---

## 6. The 45-product table

Brand is `DigiKitPro` for all 45 (these are your own private-label products).
GTIN and MPN are empty for all 45 because none exists — no placeholder, no slug
reused as an identifier. `id_exists` is therefore `no` throughout.

| # | Product id | Title in feed | Changed | Google category (id) | Brand | GTIN | MPN | id_exists |
|---|---|---|---|---|---|---|---|---|
| 1 | `portrait-skin-brushes-procreate` | **19 Portrait Skin Texture Brushes for Procreate** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 2 | `artista-studio-kit-76-brushes` | Artista Studio Kit: 76 Procreate Brushes | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 3 | `portrait-mastery-kit-46-brushes` | **Portrait Mastery Kit: 46 Procreate Brushes + 4 Paper Textures** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 4 | `essential-line-art-sketch-kit` | Essential Line Art & Sketch Kit for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 5 | `ultimate-portrait-mastery-bundle` | **Ultimate Portrait Mastery Bundle: 4 Procreate Brush Kits** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 6 | `anime-soft-style-studio-kit` | Anime Soft-Style Studio Kit: 100+ Procreate Brushes | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 7 | `glitter-brushes-sparkle-shine-30` | 30 Glitter Procreate Brushes: Sparkle & Shine Set | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 8 | `watercolor-studio-kit-50-brushes` | 50+ Realistic Watercolor Studio Kit for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 9 | `professional-digital-sketchbook` | Professional Digital Sketchbook for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 10 | `liner-marker-studio-39-brushes` | **Liner & Marker Studio: 39 High-Fidelity Procreate Brushes** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 11 | `professional-charcoal-studio` | Professional Charcoal Studio for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 12 | `male-pose-brushes-figure-drawing` | Male Pose Procreate Brushes: Figure Drawing Stamps | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 13 | `female-pose-brushes-figure-drawing` | Female Pose Procreate Brushes: Figure Drawing Stamps | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 14 | `procreate-mega-bundle-650` | 650 Procreate Brushes Mega Bundle | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 15 | `dreamy-pastel-art-kit` | The Dreamy Pastel Art Kit for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 16 | `hair-hairstyle-stamp-kit` | **Professional Hair & Hairstyle Stamp Kit for Procreate: 160 Stamps** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 17 | `premium-texture-effects-10-brushes` | 10 Premium Procreate Brushes Set: Texture & Effects | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 18 | `premium-hair-brushes-10` | 10 Premium Hair Brushes for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 19 | `master-library-2000-brushes` | The DigiKitPro Master Library: 2,000+ Procreate Brushes | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 20 | `tattoo-artist-studio-kit-200` | Tattoo Artist's Studio Kit: 200+ Procreate Brushes | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 21 | `brush-palette-bundle-160` | Procreate Brush & Color Palette Bundle: 160 Brushes + 12 Palettes | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 22 | `koi-fish-tattoo-brushes` | Koi Fish Tattoo Procreate Brushes | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 23 | `animal-fur-brushes-2` | **Animal Fur 2: 35 Procreate Brushes for Fur, Hair & Feathers** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 24 | `illustration-brushes-2` | **Illustration Brushes 2 for Procreate: 15 Textures + 5 Palettes** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 25 | `professional-hair-brushes` | Professional Hair Brushes for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 26 | `organic-watercolor-80-brushes` | 80 Organic Brushes: Watercolor Studio Kit for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 27 | `anime-soft-style-brushes-100` | **100+ Anime Soft-Style Procreate Brushes: Watercolor, Shading & Line Art** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 28 | `sketchbook-traditional-media-kit` | Professional Sketchbook Procreate Brushes: Traditional Media & Drawing Kit | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 29 | `procreate-palettes-bundle-50` | **Procreate Color Palettes Bundle: 50 Sets, 1,500 Swatches** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 30 | `master-vault-1000-brushes` | Master Vault Mega Bundle: 1,000+ Procreate Brushes | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 31 | `master-line-art-vault-300` | **Master Line-Art Vault: 300+ Fine Line Procreate Brushes** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 32 | `mindfulness-system-planner` | **10-Minute Daily Mindfulness Planner: 57-Page Hyperlinked PDF** | yes | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 33 | `wellness-journal-2026` | **2026 Digital Wellness Journal: Hyperlinked PDF** | yes | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 34 | `wellness-fitness-planner-goodnotes` | Digital Wellness & Fitness Planner for GoodNotes | no | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 35 | `adhd-planner-2026` | **2026 ADHD Balanced Mind Planner & Wellness Journal: 55-Page PDF** | yes | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 36 | `japanese-watercolour-collection` | **Japanese Watercolour Collection: 43 Illustrations + PNG Patterns** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 37 | `wellness-journal-365` | **365-Page Digital Wellness Journal: Hyperlinked PDF, Dark Mode** | yes | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 38 | `pro-sketch-traditional-art-kit` | Pro-Sketch Traditional Art Kit for Procreate | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 39 | `smoke-brushes-12` | Smoke Procreate Brushes: 12 Realistic Smoke Effects | no | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 40 | `kdp-templates-bundle-100` | 100+ Editable KDP Templates 2026: Canva Bundle | no | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 41 | `tie-dye-brushes-studio` | **Tie-Dye Brushes Studio for Procreate: 21 Brushes & Stamps** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 42 | `christmas-brushes-bundle` | **Christmas Procreate Brushes & Stamps Bundle: 173 Brushes + 44 Washi Tapes** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |
| 43 | `undated-planner-dark-mode` | **Undated Digital Planner: Dark Mode, Hyperlinked PDF + 1,000 Stickers** | yes | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 44 | `ultimate-fitness-planner` | **Ultimate Fitness Planner for Peak Performance: Digital PDF** | yes | Document Templates (`8022`) | DigiKitPro | — | — | no |
| 45 | `halloween-pumpkin-bundle` | **Halloween Pumpkin Bundle: 20 PNG Illustrations at 300 DPI** | yes | Digital Artwork (`500046`) | DigiKitPro | — | — | no |

Non-eligible items, for completeness: `free-fine-liner-brushes-100`,
`free-chalkboard-artists-toolkit`, `free-color-vault-1200-swatches`,
`procreate-starter-guide-free-ebook` (free), `procreate-portrait-masterclass-ebook`
and `morocco-7-day-itinerary` (books / guide). All keep their organic pages.

---

## 7. What still needs you

1. **Confirm the fetch in the Merchant Center UI** (`Products > Feeds` →
   `PRODUCTS SOURCE 1`). Expect the item count to stay at 45 and new attributes
   to appear on the product detail pages. If a fetch error appears, it will name
   the field — send it to me and I'll fix the generator, not the output.
2. **Read back one category** (`portrait-skin-brushes-procreate` should show
   *Software > Digital Goods & Currency > Digital Artwork*). If Google overrides
   it, tell me and I'll change the mapping.
3. **Reconcile the 3 vs 0 clicks** yourself: same date range, and check whether
   the view is *Free listings* or *All marketing methods*. Screenshot both.
4. **Decide on the planner category** — `Document Templates` is my best available
   node, but if you'd rather planners sit under a productivity-software node,
   that is a one-line change.
5. **Reviews / ratings feed** is the single biggest free-listing lever you're not
   using, and it needs real customer reviews — not something I can generate.

## 8. How to judge this in 28 and 90 days

Baseline (28 days to 2026-11-07, from your dashboard): **3 clicks**, impressions
not reported. Write the impression number down before you judge anything — you
cannot measure an improvement against a metric you never captured.

Then compare, same window, same marketing-method filter:

| Metric | Where | Why it moves |
|---|---|---|
| Impressions by `custom_label_0` | Merchant Center reports | Tells you whether planner or brush listings respond first |
| Clicks / CTR | Merchant Center reports | Only meaningful once impressions exist |
| Landing-page sessions by product | Site analytics | Separates "Google found us" from "Google converted us" |
| Completed Payhip orders | Payhip | The only number that pays |

Do not expect this to move in week one: a daily fetch plus Google's own
reprocessing means the first full comparison window starts ~1 week after deploy.

---

## 9. Short instruction to paste into the Merchant Center assistant

Keep it to this — long prompts invite invented reports:

> The product data now comes from my feed `https://digikitpro.shop/google-merchant-feed.xml`,
> which I maintain myself. Do not generate recommendations that assume account
> access you don't have; if you can't read a number, say so.
>
> Do three things only:
> 1. For each of my 45 items, report impressions, clicks and CTR for the last 28
>    and 90 days, filtered to Free listings.
> 2. List any item Google has disapproved, limited, or categorised differently
>    from its feed value, with the exact diagnostic message.
> 3. Tell me which items got zero impressions and whether the reason is
>    eligibility, category, or no search demand.
>
> Do not propose attribute rules, supplemental feeds or shipping changes: I edit
> the feed at source. Do not change prices, URLs or products.

---

## Files touched

| File | Change |
|---|---|
| `tools/merchant_feed.py` | New: verified category/title loading, highlights, detail rows, reporting labels. Fails loudly on an unverifiable category. |
| `tools/pages_misc.py` | Feed emits the four new field groups; warns when a product has no reviewed category instead of guessing one. |
| `data/merchant-categories.json` | New: 45 reviewed categories with a recorded reason each. |
| `data/merchant-titles.json` | New: 20 reviewed titles with a recorded reason each. |
| `data/google-taxonomy-nodes.json` | New: vendored official taxonomy subset (2 nodes) for offline verification. |
| `tools/qa_product_editorial.py` | Replaced "no category may exist" with "every item needs a reviewed, verified, non-blanket category". |
| `tools/qa_merchant_feed.py` | +5 tests: verified categories, Google field limits, no unbacked title claims, label segmentation, loader rejects bad data. |
