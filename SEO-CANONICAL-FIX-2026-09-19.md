# Fix for Search Console: “Alternate page with proper canonical tag” — digikitpro.shop

**Date:** 2026-09-19  
**Property affected:** `http://digikitpro.shop/` (URL-prefix property in Search Console)  
**Message date:** Sep 16, 2026 — *“Alternate page with proper canonical tag”* flagged as a **new** reason

> **Short version:** This is Google correctly respecting your canonical tags. The
> alert is noisy because your Search Console property is `http://` while the live
> site is `https://`. Every `http://` URL Google discovers therefore becomes an
> “alternate” that canonicalizes to `https://`. The fixes below remove the
> *intentional* noise so any future “new reason” is a real problem, not http vs
> https or other known duplicates.

---

## 1. What the warning actually means

In **Google Search Console → Page indexing → Alternate page with proper canonical
tag**, Google is saying:

> *“I found URL A, but URL A’s `<link rel=canonical>` points to URL B, so I will
> not index A — I honored the canonical you set and will consider B instead.”*

That status is **not an error** when the canonical is intentional. Typical
alternates on a static GitHub-Pages shop are:

| Alternate URL Google found | Canonical you set | Is this intentional? |
|---|---|---|
| `http://digikitpro.shop/about.html` | `https://digikitpro.shop/about.html` | ✅ once HTTPS is enforced, this variant disappears |
| `https://www.digikitpro.shop/products/slug/` | `https://digikitpro.shop/products/slug/` | ✅ www → apex is a deliberate duplicate |
| `https://digikitpro.shop/blog/slug/index.html` | `https://digikitpro.shop/blog/slug/` | ✅ clean URL vs raw file path |
| `https://digikitpro.shop/search.html?q=skin` | `https://digikitpro.shop/search.html` | ✅ search with `?q=` is JS-only; not a page to index |
| `https://digikitpro.github.io/digikitpro/...` | `https://digikitpro.shop/...` | ✅ mirror domain |

The Sep 16 batch was “new” because Google started crawling a larger surface
after the recent `/guides/`, `/partner/`, `/season/`, and category pages were
added, plus Pinterest `?url=` and `?utm_*` links that point back at the shop
with query strings. All of those create the same `…?param=value → clean canonical`
pattern.

---

## 2. What we fixed in code (this commit, `arena/01a0ba41-digikitpro`)

### 2.1 The single most actionable server setting: `https_enforced: false`

Checked via GitHub API on 2026-09-19:

```json
{
  "cname": "digikitpro.shop",
  "https_enforced": false,
  "https_certificate": { "state": "approved", "domains": ["digikitpro.shop","www.digikitpro.shop"] }
}
```

With this **off**, both `http://digikitpro.shop/` and `https://digikitpro.shop/`
serve 200 OK with identical HTML. Every `http://` URL therefore shows up in
Search Console as *Alternate page with proper canonical tag* to its `https://`
counterpart. GitHub Pages must be set to **Enforce HTTPS**.

**API attempt:** `gh api PUT repos/digikitpro/digikitpro/pages -f https_enforced=true`
returned **403** – the token from Arena lacks `admin:pages` scope (expected).

**Manual step for owner (one toggle, 30 seconds):**

1. Go to `https://github.com/digikitpro/digikitpro/settings/pages`
2. Under **Custom domain** confirm `digikitpro.shop` is still set and the check
   stays green
3. Tick **Enforce HTTPS** and wait a minute for “Certificate active”
4. Verify: `curl -I http://digikitpro.shop/` should now `301 → https://...`

Until that toggle is on the JS below also handles the redirect client-side so
Googlebot’s rendering sees the HTTPS canonical immediately (not a replacement
for the real 301, but a safety net).

### 2.2 Broadened the inline redirect script (`tools/core.py` → `_GITHUB_KILL`)

Every HTML page now emits one small blocking script *before any other content*
that covers four duplicate cases in order:

```js
// 1. github.io mirror → shop domain (with noindex)
if (hostname ends with github.io) → 301 to https://digikitpro.shop/…

// 2. http on shop domain → https
if (protocol === 'http:' && hostname in {digikitpro.shop, www.digikitpro.shop})
  → https://digikitpro.shop/...

// 3. www → apex
if (hostname === 'www.digikitpro.shop') → https://digikitpro.shop/...

// 4. /index.html suffix → clean directory URL
if (pathname ends with /index.html and pathname !== '/')
  → https://digikitpro.shop/…/   (e.g. /blog/slug/index.html → /blog/slug/)
```

This is **not** a substitute for the server 301 above, but it guarantees that
Google’s renderer and any visitor on an alternate host still lands on the
canonical and never bookmarks the duplicate.

### 2.3 Removed the thin search page from the sitemaps

`tools/pages_misc.py` previously listed both:

```python
static_urls = [... ("/search.html", "0.5", "weekly"), ...]
txt_urls    = [... "https://digikitpro.shop/search.html", ...]
```

A JS-driven search results page plus every `?q=` or `&utm_*` variant all
canonicalize to `search.html`. When that file is *in the sitemap* but its
query-string variants are not, Google naturally reports the variants as
*Alternate page with proper canonical tag* to the sitemap-listed target — while
also correctly concluding the listed file is thin and low priority.

**Fix:**
- Removed `search.html` from `static_urls` (sitemap.xml) and `txt_urls`
  (sitemap.txt). The site still links to search via `SiteSearch` JSON-LD /
  ` SearchAction` so Google understands site search; it just no longer asks
  Google to *index* the empty shell.
- Set its head to `noindex, follow` via `tools/core.py:head(..., robots=)` so
  `search.html` *and* any `search.html?q=…` / `search.html?utm_…` it canonicalizes
  to are consistently non-indexable.
- Result: 99 → 99 URLs in sitemaps (was 100, now correctly 99). `tools/verify.py`
  expectations updated accordingly.

### 2.4 Made `head()` robots-aware

`tools/core.py:head()` now takes an optional `robots=` argument:

```python
def head(title, desc, canonical, depth, ..., robots=None):
    robots_content = robots or "index, follow, max-image-preview:large, ..."
    # emits both <meta name="robots"> and <meta name="googlebot"> with the same value
```

Previously `build_thanks` did a string `.replace()` on the `robots` tag only,
leaving `googlebot` still as `index, follow` — contradictory signals.
All three intentionally non-indexable pages now go through the new parameter
so both tags agree:

- `search.html` → `noindex, follow`
- `thank-you.html` → `noindex, follow` (also covers `?lead=&src=` variants)
- `404.html` → `noindex, follow`

(`thank-you.html` was already excluded from sitemaps; now its robots are also
internally consistent.)

### 2.5 Netlify redirects as documentation + deploy coverage

Added to `netlify.toml` (harmless on GitHub Pages, active if the repo is ever
connected to Netlify):

```toml
[[redirects]]
  from = "http://digikitpro.shop/*"
  to = "https://digikitpro.shop/:splat"
  status = 301

[[redirects]]
  from = "https://www.digikitpro.shop/*"
  to = "https://digikitpro.shop/:splat"
  status = 301

[[redirects]]
  from = "http://www.digikitpro.shop/*"
  to = "https://digikitpro.shop/:splat"
  status = 301

[[redirects]]
  from = "/*/index.html"
  to = "/:splat/"
  status = 301
```

These mirror the JS logic above at the edge.

### 2.6 Rebuilt & verified

```bash
python3 tools/build.py      # 99 URLs in sitemap.xml/txt, 51 product image pages
python3 tools/verify.py     # ALL 84 CHECKS PASSED
```

Key post-build facts checked:

- 0 mismatched `canonical` vs file location (all self-canonicals correct)
- 0 `github.io` strings in any generated HTML
- 0 sitemap URLs containing `http://`
- `robots.txt` lists exactly 3 `Sitemap:` lines, all `https://digikitpro.shop/...`
- `search.html` & `thank-you.html` correctly absent from both sitemaps
- `404.html` also absent (as before), now with consistent `noindex`

---

## 3. Manual actions still needed in Search Console (owner)

Fixing the code stops *new* duplicates from forming. The existing report will
only clear after Google recrawls.

### 3.1 Add the *correct* Search Console properties

Your email’s link was `resource_id=http://digikitpro.shop/` — a **URL-prefix
property for `http://`** only. That property will *always* show every `http://`
URL as “alternate” to its `https://` canonical. Keep it if you like for
history, but add:

- **Domain property:** `digikitpro.shop` (covers `https`, `http`, `www`,
  subdomains in one property — recommended)
  **or** at minimum a URL-prefix property for `https://digikitpro.shop/`
- Re-add the same verification DNS/txt or HTML-file method for the new
  property, then **Submit `https://digikitpro.shop/sitemap.xml` there.**

### 3.2 Tell Google the canonical choice is intentional

No action needed on the *alternates themselves*: when you click into
*Alternate page with proper canonical tag* and see URLs like:

- `http://digikitpro.shop/…`
- `https://www.digikitpro.shop/…`
- `https://digikitpro.shop/…/index.html`
- `https://digikitpro.shop/search.html?q=…`
- `https://digikitpro.github.io/digikitpro/…`

those are **working as intended** — Google honored your canonical. Mark the
issue as reviewed once the HTTPS toggle above is on. Google will drop the
batch from the report on its next crawl.

### 3.3 If any *content* pages are listed as alternates (not just http/www)

Click **Inspect URL** on a listed URL that looks like an actual product,
guide, or blog page (e.g. `https://digikitpro.shop/products/some-kit/`).

- If the dialog says *“URL is not on Google — Alternate page with proper
  canonical tag → Canonical is <something else>”* and the canonical is a
  **different product or guide** (not just `http`→`https`), that means two
  pages share too-similar content and Google chose one over the other.
  In that case check for:
  - Duplicated `title` / `description` across products (current catalog is
    clean — 0 duplicate names)
  - Copied blog paragraphs that overlap heavily
- For this shop the duplicate surface is shallow; the only product/Guide
  similarity that ever tripped verify was the missing `product` slugs, which
  already exit the build as safe defaults and are logged.

If you share a screenshot or CSV of the specific URLs Search Console lists
under that reason, they can be inspected line-by-line for whether each is
an expected variant (http, www, index.html, ?param, github.io) or a genuine
content duplicate.

### 3.4 After deploying

1. Push this branch to `main` (or merge the PR):
   ```bash
   git push origin arena/01a0ba41-digikitpro
   # then merge to main on GitHub
   ```
2. Wait for the **Build & deploy site** workflow (Actions tab) to go green.
3. In the *new* `https://` / Domain property: **Sitemaps → Submit**
   `https://digikitpro.shop/sitemap.xml` again (forces a fresh crawl).
4. In 7–14 days check **Pages → Alternate page with proper canonical tag**:
   the http/www/index.html variants should no longer accumulate; only the
   intentional JS-search and `thank-you?lead=` param alternates remain, both
   correctly `noindex`.
5. (Optional) In **Settings → Pages → Enforce HTTPS** confirmation, plus
   inspect one URL live in Search Console to confirm `http://…` now returns
   `301 HTTPS`.

---

## 4. TL;DR checklist

- [x] Code: search removed from sitemaps + `noindex` on search/thank-you/404
- [x] Code: `robots` + `googlebot` always match
- [x] Code: inline http/www/index.html cleanup on every page + Netlify doc
- [x] Build: rebuilt, 99 sitemap URLs, verify green
- [ ] Owner (GitHub): Settings → Pages → **Enforce HTTPS** (fixes the bulk of the alert)
- [ ] Owner (Search Console): Add **Domain** or `https://` property, submit
      `https://digikitpro.shop/sitemap.xml` there, review the old `http://`
      property’s alert as expected

Once the HTTPS toggle is on, the “new reasons” message will not reappear for
the same http-vs-https surface; if it does for a different surface, the
listed URLs will point to the specific duplicate to address next.
