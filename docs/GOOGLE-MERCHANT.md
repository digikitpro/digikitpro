# Google Merchant Center product sync

## What this integration does

`tools/build.py` generates a public RSS/XML product source at:

```text
https://digikitpro.shop/google-merchant-feed.xml
```

The source is rebuilt from `data/products.json` on every site build and contains
currently available non-book products. It includes free downloads at `0.00 USD`
with `in_stock` availability. The two products in `Guides & eBooks` are held
out of this initial source pending a separate review of book identifiers and
Google destination eligibility. The existing `pinterest-feed.xml` is a separate
feed and should not be selected for Merchant Center.

Product links always point to the DigiKitPro product page. That page's Buy
buttons continue to open Payhip; the feed does not expose Payhip as the product
landing URL or claim that Payhip is the Merchant Center website.

## Connect it in Merchant Center

After this change has been deployed to the live site:

1. In Merchant Center, verify and claim `https://digikitpro.shop` under **Business
   info / Online store**. The account ID alone is not an authorization token; no
   credentials belong in this repository.
2. Go to **Products → Data sources → Add product source → Add products from a
   file** and choose the URL/scheduled-fetch option.
3. Enter `https://digikitpro.shop/google-merchant-feed.xml`, choose English, and
   select the countries you actually sell to. Schedule a daily fetch.
4. Configure account-level shipping/delivery for digital products as zero cost
   in each target country where Google requires shipping data. There is no
   physical shipment. Do not add Payhip as a separate product URL.
5. Start with free listings and review **Products → Needs attention** after
   Google processes the source. Only enable Shopping Ads for products that
   Google marks eligible. This source intentionally excludes eBooks; Google has
   a separate Shopping Ads restriction for eBooks and digital books.

Google may take time to fetch and review the source. The feed being accepted
as XML does not itself guarantee product approval or impressions.

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

The feed emits an identifier only when it is explicitly present. Google's
product/category rules and the Merchant Center diagnostics remain authoritative;
check the account's item-level feedback before enabling ads. eBooks should be
reviewed separately and are not in this initial feed.

## Local QA

```bash
python3 tools/build.py
python3 tools/verify.py
```

The verification suite parses the generated XML and checks coverage, stable
IDs, prices, images, product landing URLs, availability, the eBook exclusion,
and the matching Product structured data on product pages.
