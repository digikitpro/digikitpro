# Policy reference document

Every recommendation in this audit traces to one of these pages. Where a page says something
different from common SEO advice, the discrepancy is noted — those are the places the earlier
report in your transcript went wrong.

All links fetched and read on **2026-11-08**.

---

## 1. Product identifiers

| Attribute | URL | What it establishes |
|---|---|---|
| GTIN `[gtin]` | https://support.google.com/merchants/answer/6324461 | GTIN is **recommended** for products that have one; *"Only provide a GTIN if you're sure it's correct… don't guess or make up a value."* **Also:** under *Books and media*, *"You must provide a GTIN for non-physical items, such as digital downloads."* — the exception that applies to ebooks, not to brush packs. |
| MPN `[mpn]` | https://support.google.com/merchants/answer/6324482 | MPN is the **manufacturer-assigned** part number. A retailer's internal SKU is not one. It is not a substitute for a GTIN that exists. |
| brand `[brand]` | https://support.google.com/merchants/answer/6324351 | Brand identifies the product's brand owner; required for new products. Your own private-label products legitimately carry `DigiKitPro`. |
| identifier exists `[identifier_exists]` | https://support.google.com/merchants/answer/6324478 | Set `no`/`false` only when no UPI is available (custom/one-of-a-kind goods, pre-GTIN items). *"Products for which … is incorrectly set to no … and for which there is evidence that a unique product identifier exists, will receive a warning."* |
| About unique product identifiers | https://support.google.com/merchants/answer/160161 | Overview of which combination Google wants (GTIN, or brand + MPN). |
| How to fix: missing or incorrect GTIN | https://support.google.com/merchants/answer/14899834 | The diagnostic you would see; confirms brand + (GTIN or MPN) is the expected pairing. |

**Conclusion for DigiKitPro:** blank GTIN and blank MPN with `identifier_exists=no` is correct and
defensible *today*, because no manufacturer identifier exists for these files. If you later assign
your own MPNs as the manufacturer, switch to `brand + mpn` and `identifier_exists=yes`.

---

## 2. Categories

| Attribute | URL | What it establishes |
|---|---|---|
| Google product category `[google_product_category]` | https://support.google.com/merchants/answer/6324436 | **Optional.** *"All products are automatically assigned a product category."* An explicit value is an **override**, accepted only for: category-specific attribute requirements, Shopping campaign targeting, alcohol. Also lists the official taxonomy downloads. |
| Official taxonomy file | https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt | The authoritative list. Version used here: `Google_Product_Taxonomy_Version 2021-09-21`. |
| product type `[product_type]` | https://support.google.com/merchants/answer/6324406 | Your own category; the recommended place for catalogue structure when no Google node fits — which is the situation for digital brushes. |

**Conclusion:** there is no digital-brush node; the nearest literal node is a physical paintbrush
(ID 18). The `Software > Digital Goods & Currency` branch is the closest defensible home, but the
override is *optional and not clearly one of the three accepted cases* — hence the verification gate
in the action plan.

---

## 3. Shipping and free listings

| Page | URL | What it establishes |
|---|---|---|
| Free listings for products | https://support.google.com/merchants/answer/13889434 | Free listings appear in Search, Shopping tab, Images, Lens, YouTube, Maps, Gemini. Eligibility requires policy compliance **and** *"You're required to set up 'Shipping' settings or add shipping costs using the shipping [shipping] attribute"* in a list of countries **including the United States**. No digital-goods exemption is stated on that page. |
| shipping `[shipping]` | https://support.google.com/merchants/answer/6324484 | Per-item shipping override: service, price, country, handling and transit times. **Crucially, under "Free shipping, software subscriptions, and downloads":** *"Submit shipping cost as 0 … when advertising an intangible product such as a software subscription, digital content, or downloadable software."* The worked example is `Shipping [shipping] · US:::0 USD` — country and price, **no handling or transit time**. |
| How to fix: missing shipping sub-attribute | https://support.google.com/merchants/answer/10538141 | Delivery estimates need `max_handling_time`, `max_transit_time` and `price` together — precisely the fields that would be *fabricated* for a download. |

**Conclusion:** US shipping configuration is required, and Google documents exactly how to express a
download: **country + 0 cost, no times** (`US:::0 USD`). That is not fabrication — it is the
documented pattern for intangible products. What would be fabrication is inventing handling and
transit times, which the "missing shipping sub-attribute" page expects for physical goods.

Two legitimate implementations, pick one and do not mix them: assign the **account-level digital
service**, or **submit `<g:shipping>` per item** as `US:::0 USD`. Feed-level shipping overrides
account-level settings, so submitting both without thought is how merchants end up debugging
"missing sub-attribute: country".

---

## 4. Titles, descriptions and structured listing fields

| Attribute | URL | What it establishes |
|---|---|---|
| Product data specification | https://support.google.com/merchants/answer/7052112 | Master list. Notably: `product_highlight` is Optional, **max 150 characters, 2–100 values**, *"Describe only the product itself. Don't list keywords or search terms. Do not repeat information already provided in product_detail … or description."* `product_detail` values must be **confirmed**. |
| title `[title]` | https://support.google.com/merchants/answer/6324350 | Title requirements: accurate, no promotional text, no ALL CAPS. |
| description `[description]` | https://support.google.com/merchants/answer/6324468 | Description requirements, 5,000-character limit. |
| Create rich product description pages | https://support.google.com/merchants/answer/9479464 | **More than 4 highlights recommended; more than 5 details required.** This is the stated target the catalogue currently misses 45/45. |
| Image link `[image_link]` | https://support.google.com/merchants/answer/6324350 | Image requirements (the same page covers image specs in Merchant Center Next). |
| AI-generated content | https://support.google.com/merchants/answer/14743464 | Requires disclosure of generative-AI content, and the `structured_description` / `digital_source_type` mechanism used by this repo. |

**Conclusion:** the proposed descriptions must ship as `structured_description`
(`trained_algorithmic_media`), not as plain `description`.

---

## 5. Performance reporting (needed for the measurement plan)

Verified entry point (linked from the footer of every Merchant Center help page):
https://support.google.com/merchants/topic/11983633 — **Understand your performance**. The
impressions/clicks/CTR reports and the marketing-method filter live in the Merchant Center UI under
**Performance**, which is where the 3-vs-0 clicks question has to be settled.

*Two performance URLs that circulated earlier in this project were not re-fetched for this audit,
so they are deliberately not cited here. Reporting requirements are established by the topic link
above and by what your own account displays.*

---

## 6. Claims from the earlier transcript that these pages contradict

| Claim | Contradicting source |
|---|---|
| "Set `google_product_category` to Arts & Crafts > … > Drawing & Painting Supplies" | 6324436 (auto-assignment; override only for three cases) and the taxonomy itself — that path is physical art material. |
| "Apply `identifier_exists=no` to all items via an attribute rule" | 6324478 — the value must be true per product, and a wrong `no` with an existing UPI earns a warning. Correct answer here, but it must be derived, not bulk-forced. |
| "Configure free shipping with 0–1 day handling and 0 day transit" | **Half right, and I was wrong to reject it wholesale.** 6324484 does document a 0-cost shipping entry for downloads — but as `US:::0 USD`, without handling or transit times. The times in the original advice were the error, not the 0 cost. |
| "Supplemental data source to override feed titles" | 7052112 / general data-source behaviour — a second source of truth that silently wins over the feed, with no audit trail. |
| "Your account is healthy, 0 issues, 0 clicks" | No public source. Only your Merchant Center can answer this, and it contradicted your own dashboard. |

---

## Note on dates and drift

Google's help pages and taxonomy change. The taxonomy version used for verification is pinned in
`data/google-taxonomy-nodes.json`, and `tools/merchant_feed.py` refuses to emit a category whose id
is not in that vendored list — so if Google retires a node, the build fails loudly rather than
silently mis-filing a product.
