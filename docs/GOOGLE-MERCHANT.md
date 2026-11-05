# Google Merchant Center product sync

## What this integration does

`tools/build.py` generates a public RSS/XML product source at:

```text
https://digikitpro.shop/google-merchant-feed.xml
```

The source is rebuilt from `data/products.json` on every site build. It includes
available, **paid** non-book candidates; free/zero-price products, coming-soon
items, products in `Guides & eBooks`, ebook slugs, and the PDF travel guide are
currently excluded. These are conservative source filters, not a decision about
whether all other digital products are eligible. Google's eBook restriction
applies to Shopping ads and is not automatically a free-listings restriction.
All excluded products retain their normal site pages and Payhip links. The
Pinterest feed is separate and should not be selected for Merchant Center.

Product links point to the DigiKitPro product page. The page's Buy buttons
continue to open Payhip; the feed does not use Payhip as the product landing
URL. Google says shoppers should be able to purchase without being redirected
to a different website, while separately allowing secure third-party payment
options. The current flow's eligibility is unconfirmed; ask Merchant Center
support about it rather than assuming it is compliant or the cause of a review
delay. This feed change does not modify checkout.

## AI description provenance

Google requires descriptions created with generative AI to use
[`structured_description`](https://support.google.com/merchants/answer/6324468?hl=en)
with `digital_source_type=trained_algorithmic_media` and the original text in
`content`. Use one description attribute, not both. This applies to the feed,
not to Schema.org Product descriptions on the website.

The 2026-10-29 editorial rewrite generated the catalog's then-current `short`
and `seoDesc` text with AI. `data/merchant-ai-provenance.json` records a SHA-256
fingerprint of each of those 51 products' two exact fields. The feed selects
`short`, falling back to `seoDesc` and then `name`, as before. When the selected
field and stripped UTF-8 text match a recorded `ai` fingerprint, the generator
emits the structured AI description without changing its text. A field recorded
as verified `non_ai` is emitted as an ordinary description.

**Unknown or changed text is not assumed to be AI or non-AI.** To avoid breaking
the existing Payhip sync or dropping products, the builder retains the old
plain-description behavior and prints a warning listing affected slugs. In
GitHub Actions, it also adds a warning annotation. This does not block a build
or deployment: review the warning and determine the origin before the next
scheduled publication or Merchant fetch. A plain field is not compliant if the
unknown text was actually AI-generated. New Payhip descriptions can have
unknown provenance. Product names were not changed by the 2026-10-29 rewrite;
their original provenance is unknown, and AI-generated titles would need their
own structured-title handling. This change does not establish image provenance.

To record a **verified** source for a new or edited `short` or `seoDesc` field:

1. Determine how that exact text was created. Do not guess. If its origin is
   unknown, leave it unrecorded and investigate; do not call it `non_ai`.
2. Compute the fingerprint using the same trimming/UTF-8 rules as the feed.
   Substitute the actual slug and field in this local command:

   ```bash
   PYTHONPATH=tools python3 -c 'import json; from merchant_description import text_hash; p=next(p for p in json.load(open("data/products.json", encoding="utf-8")) if p["slug"] == "PRODUCT-SLUG"); print(text_hash(p["short"]))'
   ```

3. Under `products` in `data/merchant-ai-provenance.json`, record that slug and
   field with `"source": "ai"` for verified generative-AI text or `"source":
   "non_ai"` for text verified not to be generative-AI-created, and put the
   fingerprint in `"sha256"`. A later edit no longer matches and triggers the
   warning until reviewed again. Names used as a last-resort description are
   not currently recorded by this manifest.
4. Rebuild and run the offline checks below before any authorized publication.

See [Google's AI-generated content rules](https://support.google.com/merchants/answer/14743464?hl=en),
including its requirements for AI-generated titles and image metadata.

## Connect it in Merchant Center

After an authorized change has been deployed to the live site:

1. In Merchant Center, verify and claim `https://digikitpro.shop` under **Business
   info / Online store**. The account ID alone is not an authorization token; no
   credentials belong in this repository.
2. Go to **Products → Data sources → Add product source → Add products from a
   file** and choose the URL/scheduled-fetch option.
3. Enter `https://digikitpro.shop/google-merchant-feed.xml`, choose English, and
   select the countries you actually sell to. Schedule a daily fetch.
4. Review account-level shipping/delivery settings for digital products in each
   target country where Google requires shipping data. No physical shipment is
   involved. Do not add Payhip as a separate product landing URL.
5. Review **Products → Needs attention** after Google processes the source.
   Only enable destinations for products Google marks eligible; destination
   eligibility and account-level review are separate from valid XML.

Google may take time to fetch and review the source, and changes may extend a
pending review. Acceptance of XML does not guarantee product approval, display
or impressions. If an initial review has remained pending unusually long,
contact [Merchant Center support](https://support.google.com/merchants/gethelp).

## Product identifiers

No `gtin` or `mpn` values are currently recorded in the catalog. For entries
without either value, the generated XML says `identifier_exists=no`; that is
appropriate only when the product genuinely has no assigned GTIN/MPN. Do not
invent GTINs or reuse Payhip IDs / product slugs as GTINs or MPNs. If a product
has a valid identifier, add it to its record in `data/products.json`:

```json
{
  "gtin": "valid manufacturer-assigned GTIN",
  "mpn": "manufacturer-assigned MPN"
}
```

The feed emits an identifier only when explicitly present. Google's product and
destination rules and the account's diagnostics remain authoritative.

## Local QA

```bash
python3 tools/build.py
python3 tools/qa_merchant_feed.py
python3 tools/verify.py
```

The offline checks parse the XML, test structured descriptions, escaping,
provenance drift, unknown-source fallback and product coverage; `verify.py` also
checks prices, images, product landing URLs, availability, exclusions and
matching Product structured data. They do not access Merchant Center, verify
product eligibility or test checkout. Both existing build workflows run the
Merchant feed check after building; unknown-origin warnings remain non-blocking.
