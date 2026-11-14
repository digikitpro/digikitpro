# Pinterest catalog GPC warning — 2026-11-10

## Report and diagnosis

The supplied Pinterest catalog diagnostics show **Warning 157** (`google_product_category` missing) on products in a 50-item feed. The generator intentionally omitted this optional attribute after an earlier review rejected a blanket category. Pinterest now reports that omission as a discovery/recommendation warning. The separate **Warning 2** says the last ingestion ended early because the source had not changed; it is an informational no-op, not another product-level defect.

The source code has been updated so the CSV and XML feeds send one reviewed `google_product_category` for **each of the 50 paid products**. The category values use Google taxonomy IDs (Pinterest accepts taxonomy text values or numeric codes; see [Pinterest's catalog field reference](https://help.pinterest.com/en/business/article/before-you-get-started-with-catalogs)). The IDs and paths are checked offline against the vendored Google taxonomy subset in `data/google-taxonomy-nodes.json`.

## Mapping used

- The **48 products** already covered by `data/merchant-categories.json` reuse their reviewed per-item category: 40 downloadable brush, palette and artwork assets use `500046` (`Software > Digital Goods & Currency > Digital Artwork`); 8 planners and Canva templates use `8022` (`Software > Digital Goods & Currency > Document Templates`).
- The two paid PDF publications that are deliberately outside the common Merchant feed have Pinterest-only reviewed entries in `data/pinterest-category-extras.json`: `morocco-7-day-itinerary` and `procreate-portrait-masterclass-ebook` use `543542` (`Media > Books > E-books`). This matches their delivered format; it does not change their Merchant Center eligibility or destination.

The catalog build now fails closed if a paid Pinterest item is missing a category, an unused mapping is left behind, or an ID/path does not match the vendored taxonomy. Both `pinterest-feed.csv` and `pinterest-feed.xml` include the attribute. Feed QA checks that all 50 IDs appear in both outputs and that every category matches its reviewed mapping.

## Owner follow-up after deployment

1. After the PR is merged and the site deploys, verify that the Pinterest data source still points to `https://digikitpro.shop/pinterest-feed.xml` (or the CSV if that is the source actually connected).
2. Trigger a refresh/re-ingestion if the Pinterest UI supports it, or allow the scheduled fetch to run. The deployed file contents will differ from the previous source, so the next fetch should process the category updates rather than report an unchanged source.
3. Recheck diagnostics for 157 and also watch for **126** (category path specificity) or **158** (format). Pinterest controls validation; local XML/CSV checks do not guarantee catalog approval, distribution, or impressions.

This supersedes the prior review-build decision recorded in `docs/PRODUCT-SEO-IMPLEMENTATION-2026-10-29.md` to omit the optional Pinterest GPC. The old document remains a dated audit snapshot.

### References

- [Pinterest catalog fields and accepted GPC formats](https://help.pinterest.com/en/business/article/before-you-get-started-with-catalogs)
- [Pinterest catalog ingestion warnings](https://help.pinterest.com/en/business/article/troubleshoot-data-source-error-messages)
- [Google's English taxonomy with IDs](https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt) (the ID format avoids language-specific path differences)
