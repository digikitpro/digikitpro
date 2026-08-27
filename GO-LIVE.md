# 🚀 GO-LIVE & Google Indexing Guide (DigiKitPro)

Everything here is free. Two paths: **A** is the recommended long-term setup
(edit products/articles any time straight from your browser), **B** is a
2-minute preview.

---

## 🌐 No domain? No problem — the links fix themselves

The files you have contain a **placeholder address** (`https://digikitpro.com`)
inside `robots.txt`, `sitemap.xml` and the canonical tags. **You do not need to
buy a domain, and you must NOT edit those files by hand.** The placeholder is
replaced automatically at publish time:

- **Path A (GitHub Pages):** the deploy workflow rebuilds the site with your
  real address (`https://<username>.github.io/digikitpro-website`) on every
  change. After the first deploy, robots.txt, the sitemap and every canonical
  link are correct — zero edits.
- **Path B (Netlify connected to your GitHub repo):** our `netlify.toml` does
  the same using Netlify's own `$URL` variable. Also zero edits.
- **Netlify Drop (drag & drop only):** fine for a quick preview, but the baked
  placeholder stays. If you keep this option, build once with your address:

  ```bash
  SITE_URL="https://YOUR-SITE.netlify.app" python3 tools/build.py
  ```

  (Windows: set the variable first: `set SITE_URL=https://YOUR-SITE.netlify.app`)

Only when you later buy `digikitpro.com` do you set that domain in
`tools/core.py` and rebuild once.

---

## Path A — GitHub Pages (recommended: free hosting + edit-anytime)

You edit files on github.com → the site **rebuilds and redeploys itself**
(the workflow in `.github/workflows/deploy.yml` does it). No software on your PC.

1. **Create a free GitHub account** at github.com → "Sign up".
2. **Create the repository**: click **New repository** → name it `digikitpro-website`
   → Public → Create. *(If you also want the address* `username.github.io`
   *exactly, name the repo* `username.github.io` *— optional.)*
3. **Upload the site**. Easiest for non-coders: install **GitHub Desktop**
   (desktop.github.com) → sign in → *Add local repository* → point it at the
   unzipped `digikitpro-website` folder → *Publish repository*.
   (Power users: `git init && git add -A && git commit -m "launch" && git push`.)
4. **Turn on Pages**: on github.com open your repo → **Settings → Pages** →
   *Source:* **GitHub Actions**. Done — the first deploy starts automatically
   (check the **Actions** tab; ~1 minute).
5. Your site is live at **`https://<your-username>.github.io/digikitpro-website/`**
   — free HTTPS included.

**Add a product or article later** (the part you asked about):
- Repo → `data/products.json` → ✏️ pencil icon → copy an existing product block,
  change name/price/Payhip link → **Commit changes**. The site rebuilds itself.
- New article: `content/blog/` → **Add file → Create new file** →
  `my-article-slug.md` with front-matter like the existing ones → Commit.
- New product image: upload the `.webp` into `assets/products/<slug>/` (web UI
  limits you to 100 files per upload — images per product are only a few files).

## Path B — Netlify Drop (instant preview, no account needed to try)

1. Go to **app.netlify.com/drop** and drag the **unzipped folder** onto the page.
2. You get a live URL instantly (create a free account to keep the site, then
   *Site settings → Change site name* to e.g. `digikitpro.netlify.app`).
3. ⚠️ If you use Netlify, first tell me the final URL (or set `SITE_URL` in
   `tools/core.py` and run `python3 tools/build.py`) so canonical links and the
   sitemap point at the right domain. Editing later = re-drop the rebuilt folder
   → that’s why **Path A is better for you**.

> **Custom domain later?** Buy `digikitpro.com` (≈$10/yr) → in GitHub Pages
> settings add it, then set `SITE_URL = "https://digikitpro.com"` in
> `tools/core.py` and rebuild. Free HTTPS on both hosts.

---

## 🔎 Get indexed fast (Google Search Console)

The site already ships everything technical: `sitemap.xml` (auto-updates),
`robots.txt`, canonical tags, Product/Article/Breadcrumb JSON-LD schema, OG/Twitter
cards, semantic headings, sized lazy images. What remains is on Google’s side:

1. **Search Console**: search.google.com/search-console → **Add property →
   URL prefix** → paste your live URL (`https://…github.io/digikitpro-website`).
2. **Verify ownership** — choose **HTML tag** method, copy only the long token.
   Add it without touching code: repo → **Settings → Secrets and variables →
   Actions → Variables → New variable** → name `GOOGLE_VERIFY`, value = token →
   save → repo **Actions** tab → **Run workflow**. The tag appears on every page;
   click **Verify** in Search Console. (Same for Bing: variable `BING_VERIFY`,
   tag `msvalidate.01`.)
3. **Submit the sitemap**: left menu **Sitemaps** → type `sitemap.xml` → Submit.
4. **Request indexing**: paste your homepage URL in the top search bar →
   **Request Indexing**. Repeat for `products.html`, `freebies.html`,
   `bundles.html`, `blog.html` and your best product page. (Max ~10/day.)
5. **Bing Webmaster Tools** (bing.com/webmasters): *Sign in with Google* →
   **Import from Search Console** — one click, sitemap included. Bing feeds
   DuckDuckGo/Ecosia too.

Real acceleration levers (free):
- **Link the site from your Payhip store** (store description + each product
  description) — a live inbound link is the #1 indexing trigger.
- Add your social profiles to `SOCIAL` in `tools/core.py` and post the launch.
- Keep publishing: 1 article/week via `content/blog/` — fresh content is what
  brings crawlers back daily.

### Honest expectations
- Your **brand name “DigiKitPro”** should appear in Google within days.
- Competitive phrases (“best procreate brushes”) typically take **4–12 weeks**
  of indexing + the article library + a few inbound links.
- SEO-critical: never leave `SITE_URL` pointing at a domain you don’t use —
  it feeds canonical URLs and the sitemap. One line in `tools/core.py`, rebuild,
  done (or just tell me the URL and I’ll rebuild the package for you).
