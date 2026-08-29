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
4. **IndexNow** - optional free instant indexing for Bing/Yandex/Seznam.

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

IndexNow tells Bing, Yandex and Seznam the instant your URLs change.

1. Generate any short key, example `a1b2c3d4e5f67890`.
2. Create a repository variable **`INDEXNOW_KEY`** with that key.
3. Build/deploy. `tools/build.py` writes `<key>.txt` to the site root automatically.
4. The deploy workflow then calls `tools/submit_index.py`, which posts your products to IndexNow.

You can also run it locally:
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
