# Owner kit — First clicks: HTTPS, GSC, Pinterest, outreach (do this week)

The store's problem per today's GSC exports is not merchandising and not code — it is that Google hardly knows the site exists (6 of ~101 pages indexed; zero product-page impressions; zero clicks). Here's the whole runway, click by click. Everything below is your 15–45 minute work; none of it is optional if you want next month's numbers to look different.

## A. The two flips Google needs first (20 minutes)

1. **GitHub Pages → Enforce HTTPS.** Repo Settings → Pages. The exports show http:// URLs earning impressions, which happens when GitHub Pages serves http 200s — duplicate host, split crawl.
2. **GSC → add Domain property** `sc-domain:digikitpro.shop` (DNS TXT) or an `https://digikitpro.shop` URL-prefix property; **resubmit `sitemap.xml`** under it; keep the http property for history only.

## B. Crawl reclamation (20 minutes, after the same day)

1. GSC → Coverage (the new property) → note "Crawled – currently not indexed" URL (ID from the export: 1 page) → open URL Inspection, read why, fix or consolidate.
2. URL Inspection → **Request Indexing** for: `/` · `/products.html` · `/bundles.html` · `/freebies.html` · `/category/portrait/` · `/category/skin-texture/` · `/products/portrait-skin-brushes-procreate/` · `/products/portrait-mastery-kit-46-brushes/` · `/products/essential-line-art-sketch-kit/` · `/products/ultimate-portrait-mastery-bundle/` · `/products/free-fine-liner-brushes-100/` · the 4 impression pages (/blog/how-to-choose-procreate-brushes/, ...anime/, ...realistic-skin..., ...make-digital-art-look-traditional/).
3. Done. Re-check Coverage in 2 weeks. Success = known pages > 40, indexed > 25, product surfaces appearing with impressions.

## C. Pinterest — the channel Google isn't strangling (45 minutes, ongoing)

`https://digikitpro.shop/pinterest-feed.xml` (or .csv) is generated every build with all 50 paid products and a per-item `google_product_category` from Google's taxonomy. The category IDs use the reviewed product map; after the feed update is deployed, refresh or wait for the scheduled Pinterest source fetch so it ingests the changed rows.

1. Pinterest → Business account → Settings → Claim → verify `digikitpro.shop` (method Pinterest offers — HTML tag or DNS).
2. Pinterest → Create → **Catalogs** → connect your data source: the pinterest-feed.xml URL. Once processed, product pins become shoppable/searchable. A "no changes since the last successful update" warning is an ingestion no-op, not an item error; the category change should give the next fetch updated feed content.
3. Manual cadence to prove ROI: **2 pins/week** for 8 weeks using REAL artwork only (cover renders, before/after portraits for skin/mastery pages). Link = the PDP URL. Caption like "19 portrait-skin brushes for Procreate — pore and freckle marks, matte before/after inside" (truthful sensations, no fake stats).
4. Track: Pinterest analytics → outbound clicks → PDPs. Pins that earn saves → note and remake in that style.

## D. Outreach for the first outside links (30 minutes, 10 targets)

Nobody outside your domain has reason to link yet. Ask — honest pitch, no paid placements:

> Subject: demo GIF + an honest line for your {brush/resources} roundup?
>
> Hi {name} — I make DigiKitPro (independent, Procreate portrait brushes). I saw your roundup at {URL} — noticed {one specific detail showing you actually read it}. I'm happy to send a demo GIF of the skin-texture brushes (no obligation to include) and a one-sentence correction-tested note on what's in the pack. Free to use, credit appreciated.

Targets (existing 2026-era brush listicles/blogs — read each first, don't spray):
- bebrushes.com (brush roundups) · brusher.art (guides) · CreativeBloq's Procreate articles · ImagineFX's features · Reddit r/ProCreate (answer questions, no product drop) · r/DigitalPainting · r/ArtistLounge · Behance/ProductHunt carrier communities · the Procreate forums (community.procreate.com) · Pinterest ≥ 3 visual boards in the "procreate brushes" niche.

Success = 10 sent → 2 replies, 1 link/mention. Anything below that is normal; repeat monthly.

## E. GA4 — where the numbers already live

GA4 Measurement ID `G-5MFQFHNB6B` is wired sitewide with a custom event layer (buttons carry `data-dkp-event` attributes, e.g. buy-panel/pdp/next-step clicks, kit comparisons, freebie→paid journeys). In GA4: **Reports → Engagement → Events** — look for your CTA/Journey events and for `purchase`-adjacent outbound clicks to Payhip (GA4 can't see Payhip orders; match to Payhip sales manually). If events are empty after a week, check the tag with GA4 **DebugView** on one PDP.

## F. The weekly 10-minute ritual (Fridays)

| What | Where | Watch |
|---|---|---|
| Clicks / impressions / position | GSC → Performance (filter: Web, last 28d) | impressions rising = health; clicks > 0 = legitimacy |
| Indexed pages | GSC → Pages | coverage rising toward 25+ |
| Organic sessions → products /products/* | GA4 | trend, not level |
| Outbound-to-Payhip clicks | GA4 events | per PDP |
| Orders / revenue | Payhip | correlate with weeks of posting/outreach |

Honest expectation: first clicks will be single digits. You are earning from ~6 indexed pages with a domain Google has crawled for ~8 weeks. Weeks 2–4 after the GSC flips should show the Coverage number move; weeks 3–6 can show clicks. If Coverage stays < 20 after 4 weeks, stop posting content and fix the property/HTTPS chain instead.
