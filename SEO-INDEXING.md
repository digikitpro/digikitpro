# 🔍 DigiKitPro SEO, Indexing & International Playbook

This site already ships: sitemap.xml, robots.txt, canonical URLs, unique titles/descriptions,
Open Graph + Twitter cards, Product/Offer/Article/FAQ/Breadcrumb/ItemList JSON-LD, semantic HTML,
responsive WebP images with alt text, and clean directory URLs.

What this update adds (and how to use it):

1. **Worldwide + 7-language support** - English, Español, Français, Deutsch, Italiano, Português,
   Nederlands. Visitors see a globe button in the header; visitors whose browser isn't English get
   a one-time “Translate this page?” prompt. Marketing copy on the homepage now calls out worldwide
   instant delivery and no-shipping international checkout.
2. **Auto-trending highlights** - the homepage builds a daily-rotating “Trending in Procreate &
   Digital Art” section from your own catalog (best-sellers, bundles, freebies) plus internal
   “Trending searches” links. Products page has a **Trending** filter chip.
3. **Auto-add Payhip products** - `tools/payhip_sync.py` plus the ready-to-install
   `docs/automation/payhip-auto-sync.yml` (move it to `.github/workflows/sync-payhip.yml`).
   It reads your public Payhip store, discovers new product IDs, fetches the product
   details, adds them to `data/products.json`, rebuilds the site, and commits. Products you add on
   Payhip appear on the site automatically. (It never overwrites hand-written SEO copy.)
4. **IndexNow** - free change notifications for participating engines, including Bing/Yandex/Seznam (not a guarantee of indexing).

---

## 1. Google Search Console + Bing Webmaster Tools (one-time, ~10 min)

This uses **GitHub Actions variables**, not code edits, so you don’t break anything.

### Google
1. Go to `search.google.com/search-console` → Add property → **URL prefix** → paste your live URL
   (e.g. `https://yourusername.github.io/digikitpro-website/`).
2. Choose the **HTML tag** method. It gives you a token inside:
   `<meta name="google-site-verification" content="TOKEN">`.
3. In your GitHub repo: **Settings → Secrets and variables → Actions → Variables →
   New repository variable**:
   - **Name**: `GOOGLE_VERIFY`
   - **Value**: `TOKEN` (just the token, not the full tag)
4. Trigger a rebuild (Actions → **Build & deploy site** → *Run workflow*, or push any edit).
   The tag is added to every page automatically.
5. Back in Search Console, click **Verify**.

### Bing
1. Go to `bing.com/webmasters`. The fastest path is **Import from Google Search Console**.
2. If you want direct verification, create repository variable `BING_VERIFY` with the
   `msvalidate.01` token and rebuild.
3. Submit the sitemap in Bing Webmaster Tools too (Bing feeds DuckDuckGo/Ecosia).

### Google Analytics 4 (GA4)
1. In Google Analytics (`analytics.google.com`), go to **Admin → Data Streams → Web** and copy your **Measurement ID** (format: `G-XXXXXXXXXX`).
2. To enable tracking across every page on the site, provide your Measurement ID in one of two ways:
   - **Repository Variable (recommended)**: In GitHub repo **Settings → Secrets and variables → Actions → Variables → New variable**:
     - **Name**: `GA_MEASUREMENT_ID`
     - **Value**: `G-XXXXXXXXXX`
   - **Direct in code**: Edit `GA_MEASUREMENT_ID` in `tools/core.py`.
3. When built, the generator automatically injects the official Google tag (`gtag.js`) into the `<head>` of all 77+ pages.
4. Deploy the site, then check Google Analytics **Realtime** report to see live visitors.

### Submit the sitemap
- Google: Search Console → **Sitemaps** → add `sitemap.xml` → Submit.
- Bing: Webmaster Tools → **Sitemaps** → `sitemap.xml`.

---

## 2. IndexNow (recommended, free)

IndexNow notifies participating engines, including Bing, Yandex and Seznam, about URL changes.
Google does not use IndexNow, and an accepted notification does not guarantee crawling or indexing.

It is **on by default**: `.github/workflows/deploy.yml` and `sync-payhip.yml` carry a default key
(an IndexNow key is public by design — engines fetch it from your site — so it is not a secret).

1. Nothing to configure. To rotate the key, create a repository variable **`INDEXNOW_KEY`**; it
   overrides the default in both workflows.
2. Build/deploy. `tools/build.py` writes `<key>.txt` to the site root automatically.
3. After Pages is deployed, `tools/submit_index.py` posts new or changed eligible HTML pages,
   including `/tools/`. The daily catalog sync queues a deployment when it has changes or a
   pending IndexNow retry; it does not submit before the deployment.

The script checks actual generic `robots` meta elements in the built HTML, excluding `noindex` and
`none` pages from routine updates. It does not inspect HTTP `X-Robots-Tag` headers. Once the new v2
state is recorded, a previously tracked indexable URL is notified when its page becomes `noindex`
or disappears from the built HTML. Once accepted, later edits to a `noindex` page are not routinely
submitted. The previous v1 state did not record indexability, so earlier `noindex` transitions and
removals cannot safely be inferred during migration. A failed POST leaves state unchanged for retry;
an unreadable or invalid state stops submission rather than triggering a mass re-submit. Redirects
configured only at the server, without a detectable built-file change, are not automatically detected.

Preview the URLs selected from the local build and state without contacting IndexNow or writing state:
```bash
python3 tools/submit_index.py --dry-run
python3 tools/qa_indexnow.py  # offline regression tests
```

To submit manually, run the following **only after those pages are live**; it sends a real notification
and updates local state on success:
```bash
INDEXNOW_KEY=a1b2c3d4e5f67890 SITE_URL=https://YOUR-SITE python3 tools/submit_index.py
```

> The key file must be reachable at `https://YOUR-SITE/<key>.txt`. After the first deploy it is.

---

## 3. Auto-add a product you add on Payhip

You don’t need to edit HTML. Either let the daily workflow do it, or run it by hand:

```bash
python3 tools/payhip_sync.py      # adds/updates data/products.json
python3 tools/build.py            # regenerates product pages, sitemap, search index
```

- Install the workflow: copy `docs/automation/payhip-auto-sync.yml` to
  `.github/workflows/sync-payhip.yml` (see `docs/automation/README.md`).
- If the workflow finds new Payhip products it commits them and the deploy workflow publishes them.
- New products are added as **Trending/featured** so they appear near the top, but they are **not**
  labeled “New”.
- For full marketing polish (rich description, gallery images, FAQ, related kits), open
  `data/products.json` and enrich the entry later - the sync never deletes those edits.

---

## 4. Keep ranking up: simple editorial cadence

- Add **1 article/quarter minimum** in `content/blog/` (one file = one article, fully generated).
- After adding a product, **link it from your Payhip store description** - an inbound link from the
  store is one of the fastest indexing signals.
- Keep your Payhip store category names in English (they map to the site’s Trending topics).
- Share the site on Pinterest/Instagram/TikTok when you add a kit. Add those accounts to
  `SOCIAL` in `tools/core.py` (they then appear in the footer + Organization schema).

---

## 5. Expected timeline (honest)

- Brand “DigiKitPro” appears within days.
- Non-competitive pages (e.g. `free-procreate-brushes`, `how to install procreate brushes`) often
  index in 1–4 weeks.
- Competitive terms like “best procreate brushes” take 4–12+ weeks, depending on content depth and
  inbound links.
