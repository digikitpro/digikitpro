# Google Search Console crawl-discovery review — 2026-11-10

## Supplied report

The report shows two different statuses:

- `https://digikitpro.shop/index.html` — **Page with redirect**.
- 55 URLs — **Discovered – currently not indexed**, with `Last crawled: N/A`.

These are not the same issue. The first is an alternate homepage URL. The second means Google has discovered the URLs but has not recorded a crawl yet; it is not the same as **Crawled – currently not indexed** and does not by itself show a content-quality rejection.

## Local checks

- The canonical homepage is `https://digikitpro.shop/`. `/index.html` is intentionally not a sitemap URL, and the generated HTML contains no internal links to that alias.
- All 55 URLs in the supplied **Discovered** list are present in the XML sitemap and reachable from the homepage through ordinary internal HTML links.
- All product pages are linked from `/products.html`; all published blog articles are linked from `/blog.html`.
- `robots.txt` allows crawling and advertises the XML sitemap. The sitemap contains 109 canonical page URLs; it does not contain `/index.html`.
- The product/free-resource topic navigation now includes direct links to all ten collection categories, including Sketching, Traditional Media, Glitter & Effects, and Figure Drawing.
- `tools/qa_seo.py` now checks sitemap-to-homepage link reachability and direct product/article links from their respective index pages, so future builds catch broken discovery paths.

These are offline source/build checks, not a live fetch from Google or proof that Google will index every URL.

## Recommended Search Console follow-up

1. Keep `/index.html` redirected; inspect the canonical homepage `/` instead. Do not add `/index.html` to the sitemap or change the homepage canonical.
2. In the verified HTTPS or Domain property, confirm that `https://digikitpro.shop/sitemap.xml` is processed and has no fetch error. The XML sitemap already contains the page URLs and image entries; a separate text sitemap is not needed for this check.
3. Use URL Inspection on `/`, `/products.html`, and a small sample of priority product/article URLs. Check the live test, **Indexing allowed**, and Google's selected canonical. If the UI offers it, request indexing selectively for a few important URLs—not all 55 at once.
4. Recheck the report after Google has had time to crawl. If a live test reports a fetch, robots, or canonical error, use that exact URL-level error as the next fix; the current local audit found no missing sitemap URLs or internal crawl paths.

Submitting or requesting a URL does not guarantee crawling or indexing. The sitemap's `priority` and `changefreq` values cannot force faster crawling, and no fabricated `lastmod` dates have been added.

## Validation run

- `python3 tools/verify.py` — 115/115 passed.
- `python3 tools/qa_seo.py` — 3,794 checks passed across 112 pages, 109 sitemap URLs, 197 sitemap images, and 22 articles.
- `python3 tools/qa_merchant_feed.py` — 18/18 passed.
- `python3 tools/qa_assets.py` — 0 missing assets.
- `python3 tools/qa_form.py` — passed.
- `python3 tools/qa_guide_accuracy.py` — 7/7 passed.
