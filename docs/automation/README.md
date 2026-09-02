# DigiKitPro - GitHub Actions automation

**Status (re-verified 2026-09-02):** the `workflows` permission is **granted**.
A push that added `.github/workflows/sync-payhip.yml` was accepted, so this
assistant can create and update workflow files directly. The limitation
documented here before 2026-09-02 no longer applies.

## What is installed and running

| Workflow | File | Trigger | What it does |
|---|---|---|---|
| Build & deploy site | `.github/workflows/deploy.yml` | push to `main`, manual | `tools/build.py` then deploys to GitHub Pages |
| Auto-sync new Payhip products | `.github/workflows/sync-payhip.yml` | daily 06:30 UTC, manual | `tools/payhip_sync.py`, `tools/seo_engine.py`, `tools/build.py`, commit, IndexNow ping |

Together these mean: add a product in Payhip and it appears on the site within a
day, with keywords and descriptions generated automatically. No manual step.

## The SEO engine

`tools/seo_engine.py` generates, for each product:

| Field | Used by | Cap |
|---|---|---|
| `keywords` | reference and export only | 14 terms |
| `tags` | card `data-tags` filtering, category hubs, `js/search-index.js` | 14 terms |
| `seoTitle` | page `<title>` | 70 chars, brand suffix kept |
| `seoDesc` | meta description | 165 chars |
| `short` | product page blurb and card alt text | 155 chars |
| `alt` | product gallery image alt text | 110 chars |

`tags` is the field that matters most. `tools/core.py`, `tools/pages_category.py`
and `tools/pages_misc.py` all read it, so a product with empty tags is invisible
to on-site search, filtering and the category hubs.

Three rules it follows:

1. **Deterministic and offline.** No API key, no network, no model call. The
   same product always yields the same copy, so CI stays reproducible.
2. **Hand-written copy is never overwritten.** A field is filled only when it is
   missing, empty, or still holds a value this engine or `payhip_sync.py`
   generated. The only exception is a product marked `"auto": true`, which is
   machine owned and regenerated freely.
3. **Limits match the house style** already in `data/products.json` rather than
   generic SEO advice, so generated copy reads like the records around it.

```bash
python3 tools/seo_engine.py                  # fill gaps on auto products
python3 tools/seo_engine.py --all            # fill gaps across the catalogue
python3 tools/seo_engine.py --all --dry-run  # report only, write nothing
python3 tools/seo_engine.py --check          # exit 1 if any field is missing
```

## Still optional: IndexNow on every deploy

`deploy.patched.yml` adds an IndexNow step to the build and deploy workflow so
every publish pings Bing, Yandex and Seznam. It is **not applied yet**, because
it changes the workflow that publishes the live site.

To apply it by hand: repo → `.github/workflows/deploy.yml` → pencil → paste the
contents of `docs/automation/deploy.patched.yml` → Commit.
Or locally: `git apply docs/automation/deploy-indexnow.patch`.

## Required repository variables

**Settings → Secrets and variables → Actions → Variables**

| Variable | Needed for | Notes |
|---|---|---|
| `INDEXNOW_KEY` | search engine pings | any 8 to 128 character hex string |
| `GOOGLE_VERIFY` | Search Console meta tag | optional |
| `BING_VERIFY` | Bing Webmaster meta tag | optional |

Without `INDEXNOW_KEY` both workflows still run, the ping step is simply skipped.

## Local equivalents

```bash
python3 tools/payhip_sync.py                 # pull new Payhip products into data/products.json
python3 tools/seo_engine.py --all            # fill in keywords, tags, titles, descriptions
python3 tools/build.py                       # rebuild every page plus sitemap
INDEXNOW_KEY=... python3 tools/submit_index.py   # ping Bing / Yandex / Seznam
```

## Notes for maintainers

- `data/payhip_sync_report.json` is gitignored. It is rewritten on every sync
  with a fresh `checked_at` timestamp, so tracking it would produce an empty
  commit every single day.
- `tools/payhip_sync.py` writes `data/products.json` with `indent=2`, matching
  the committed file. Changing that rewrites the whole file as a spurious diff.
- `tools/pages_blog.py` sorts articles by filename before sorting by date, so
  posts published on the same day keep a stable order across machines.
