# DigiKitPro — GitHub Actions automation (bring-your-own-workflow)

This PR couldn't push the files inside `.github/workflows/` directly because the
GitHub App token used here doesn't have the `workflows` permission. That's a
GitHub-side permission, not a code problem.

The automation itself is complete and tested to compile — you just need to
place the workflow files in your repo. Two files were prepared here:

| File | What it does | Where it should live |
|---|---|---|
| `docs/automation/payhip-auto-sync.yml` | Daily/on-demand sync of new Payhip products → `data/products.json`, rebuild, commit | `.github/workflows/sync-payhip.yml` |
| `docs/automation/deploy-indexnow.patch` | Adds `INDEXNOW_KEY` to the deploy build and pings Bing/Yandex/Seznam after deploy | Apply to `.github/workflows/deploy.yml` |

## Quick install (single user, no permission changes needed)

1. Open the repo on GitHub → go to `.github/workflows/` → **Add file → Create new file**.
2. Name the file `sync-payhip.yml`, paste the entire contents of
   `docs/automation/payhip-auto-sync.yml`, and commit it.
3. If you want IndexNow instant indexing, also update `deploy.yml` with the two
   blocks shown in `docs/automation/deploy-indexnow.patch` (the `INDEXNOW_KEY`
   env var and the final "Ping search engines (IndexNow)" step).
4. Go to **Settings → Secrets and variables → Actions → Variables** and add:
   - `INDEXNOW_KEY` = any short key (e.g. `a1b2c3d4e5f67890`)
   - `GOOGLE_VERIFY` = token from Google Search Console (optional)
   - `BING_VERIFY` = token from Bing Webmaster Tools (optional)
5. Run the new **Auto-sync new Payhip products** workflow once from the Actions tab.

## Alternative (best): grant the GitHub App `workflows` permission

If you want future PRs from this assistant to be able to create/update workflow
files, grant the GitHub App **Read and write → Workflows** permission in the
repository/installation settings. After that, this automation can be moved back
into `.github/workflows/` normally.

> The core code behind every workflow (`tools/payhip_sync.py`,
> `tools/submit_index.py`, `tools/build.py`, and all site changes) is already in
> this PR and does not need any permission.
