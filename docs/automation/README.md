# DigiKitPro — GitHub Actions automation (bring-your-own-workflow)

**Status (re-verified 2026-08-27):** the GitHub App token used by this assistant
still does **not** have the `workflows` permission. A push that added
`.github/workflows/sync-payhip.yml` and updated `.github/workflows/deploy.yml`
was rejected by GitHub with:

```
! [remote rejected] refusing to allow a GitHub App to create or update workflow
  `.github/workflows/deploy.yml` without `workflows` permission
```

That is a GitHub-side permission, not a code problem. Everything the workflows
call (`tools/payhip_sync.py`, `tools/submit_index.py`, `tools/build.py` and all
site changes) is already merged into `main` and needs no permission at all —
only the two YAML files below have to be placed by a human (or by this
assistant once the permission is granted).

## Files in this folder

| File | What it does | Where it should live |
|---|---|---|
| `payhip-auto-sync.yml` | Daily + on-demand sync of new Payhip products → `data/products.json`, rebuild, commit, IndexNow ping | `.github/workflows/sync-payhip.yml` (new file) |
| `deploy.patched.yml` | **Complete, ready-to-paste** copy of the current `deploy.yml` *with* the IndexNow additions | replaces `.github/workflows/deploy.yml` |
| `deploy-indexnow.patch` | The same change as a diff, if you prefer `git apply` | applies to `.github/workflows/deploy.yml` |

## Option A — install by hand on github.com (2 minutes, no permission change)

1. Repo → `.github/workflows/` → **Add file → Create new file**.
   Name it `sync-payhip.yml`, paste the whole contents of
   `docs/automation/payhip-auto-sync.yml`, **Commit**.
2. Repo → `.github/workflows/deploy.yml` → pencil icon → select all → paste the
   whole contents of `docs/automation/deploy.patched.yml`, **Commit**.
   (Or locally: `git apply docs/automation/deploy-indexnow.patch`.)
3. **Settings → Secrets and variables → Actions → Variables** → add:
   - `INDEXNOW_KEY` = any 8–128 char hex string (e.g. `a1b2c3d4e5f67890`)
   - `GOOGLE_VERIFY` = token from Google Search Console (optional)
   - `BING_VERIFY` = token from Bing Webmaster Tools (optional)
4. **Actions** tab → **Auto-sync new Payhip products** → **Run workflow** once to
   confirm it is green.

## Option B — grant the App the `workflows` permission (recommended)

Repository/installation **Settings → GitHub Apps → (this app) → Configure →
Permissions → Workflows: Read and write**. After approving it, this assistant
can move both files into `.github/workflows/` itself and you never have to
copy-paste workflow YAML again.

## Local equivalents (no Actions needed)

```bash
python3 tools/payhip_sync.py     # pull new Payhip products into data/products.json
python3 tools/build.py           # rebuild every page + sitemap
INDEXNOW_KEY=... python3 tools/submit_index.py   # ping Bing / Yandex / Seznam
```
