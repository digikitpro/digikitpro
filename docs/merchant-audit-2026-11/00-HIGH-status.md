# HIGH-priority status — DigiKitPro Merchant feed

**Updated:** 2026-11-08 · Only High-severity items appear here. Medium/Low findings are in
`01-audit-report.md` and are not repeated.

---

## Fixed in code — no action needed from you

| # | High issue | Before | Now | Where |
|---|---|---|---|---|
| 1 | Titles ignored how buyers search | 11/45 lacked the platform keyword; brand-led, count-free | **45/45 rewritten**: product type first, confirmed counts where stated, 50–76 chars | `data/merchant-titles.json` |
| 2 | Descriptions were one sentence | `short` field, no format/requirements/audience | **45/45 full descriptions**, 41–66 words, disclosing AI origin via `structured_description` | `merchantDescription` per product |
| 3 | Google's rich-listing bar missed | **0/45** met >4 highlights, **0/45** met >5 details | **36/45** and **20/45** (up from zero) | `tools/merchant_feed.py` |
| 4 | No category, so Google classified `.brushset` files itself | 0/45 | **45/45**, verified against the official taxonomy, 2 nodes only | `data/merchant-categories.json` |
| 5 | No reporting segments | 0/45 | **45/45** `custom_label_0..3` (class, category, price band, priority cluster) | same |
| 6 | Compatibility stated three times | — | Once as a highlight, once as a `Requires` detail row, never in prose | `tools/merchant_feed.py` |
| 7 | Landing pages assumed healthy | unverified | **45/45 verified**: indexable, canonical, price matches page *and* structured data, image resolves, Payhip link present | `05-landing-evidence.csv` |
| 8 | Tests could not catch drift | — | 15 merchant tests incl. coverage floors, verbatim-repetition ban, unbacked-number ban | `tools/qa_merchant_feed.py` |
| 9 | Two counts confirmed by owner and applied | Both listings said "count awaiting confirmation" | `essential-line-art-sketch-kit`: **43 brushes + 1 bonus texture brush** (14 pencil, 12 liner, 7 ink, 6 detailers, 3 sketch tools); `ultimate-portrait-mastery-bundle`: **252+ assets across 4 kits** (43 + 19 + 160 + 30) — stated on the pages, feed titles, highlights and detail rows, sourced to the Payhip listings; detail-row parser also stopped mangling counts with a trailing `+` (it was emitting junk rows like `0 / 65` for `650+ brushes`) | `data/products.json`, `data/merchant-titles.json`, `tools/merchant_feed.py`, `tools/qa_product_editorial.py` |

Feed: **44** items (`pro-sketch-traditional-art-kit` held out 2026-11-08, see H). All suites pass — 18 merchant tests, 1,234 editorial checks, 115 verify checks. Items with >5 detail rows: 21/44 (was 22/45).

**Source of truth for the two confirmed counts:** the Payhip listings `https://payhip.com/b/b70QE` and `https://payhip.com/b/2h0iG` (owner-confirmed 2026-11-08). `qa_product_editorial.py` now asserts the counts are present and the old "disputed count" ban / mandatory "awaiting confirmation" caveat were retired.

---

## Still High, and genuinely blocked

| # | Issue | Count | Why I can't fix it | What unblocks it |
|---|---|---|---|---|
| A | Highlights below Google's bar | **9** items | The record states fewer than 4 facts; padding means inventing | Add a fact to `features` |
| B | Detail rows below Google's bar | **23** items (was 25) | Same — no sixth stated spec exists | Add a fact to `technical` |
| C | Single-image listings | **6** items (incl. `master-library-2000-brushes`, `brush-palette-bundle-160`) | I cannot fabricate product previews | Real images |
| D | Unconfirmed brush/stamp counts | **7** products (2 of 9 confirmed 2026-11-08: `essential-line-art-sketch-kit` 43 brushes, `ultimate-portrait-mastery-bundle` 252+ assets) | Only you know the remaining numbers | Confirm each remaining count |
| E | US shipping / eligibility | all 45 | Needs your Merchant Center login | Confirm the digital service or `US:::0 USD` |
| F | Category override may impose `Software` field requirements | all 45 | Google only *accepts* overrides in 3 cases; mine is accuracy | One fetch, then keep or revert |
| G | Baseline never captured | — | No access to impressions/clicks | Export 28-day data before judging |
| H | `pro-sketch-traditional-art-kit` delivers a **RAR** archive | 1 product | iPad's Files app cannot extract RAR, and the install guide (`content/blog/how-to-install-procreate-brushes.md`) documents ZIP only — a buyer following it gets stuck at step 2. Owner-reported 2026-11-08; the catalogue's file list for this product is empty, so the RAR is also not stated anywhere on the page | Re-upload the download as a ZIP on Payhip (recommended), or document RAR extraction in the install guide; then align the product page technical row and the guide in the same change |

**A stayed at 9; B moved 25 → 23 on 2026-11-08:** the two confirmed counts lifted `essential-line-art-sketch-kit` and `ultimate-portrait-mastery-bundle` to 6 highlights and 8 detail rows each, and the detail-row parser fix let `portrait-mastery-kit-46-brushes` (6) and `anime-soft-style-studio-kit` (6) cross the bar. The parser fix also removed junk rows (e.g. `0 / 65`) from six other items.

**2026-11-08 — mitigation shipped for H, not a fix.** `pro-sketch-traditional-art-kit` is now held out of `google-merchant-feed.xml` via `FEED_HOLDS` in `tools/merchant_feed.py` (44 items in the feed). The product keeps its organic page and Payhip link; it simply no longer ships to Google while the `.rar` download is the buyer's reality, and its unverified-cover highlights (“Cover and text need owner verification”) never reach buyers. H **stays High** until the owner re-uploads a verified ZIP on Payhip and confirms the cover; the hold is lifted by deleting the one `FEED_HOLDS` entry and rebuilding. Do not re-add the product by editing generated XML.

**Unrelated finding, needs your call (2026-11-08):** buyer-visible confirmation-caveat highlights still exist on nine items — `male-pose-brushes-figure-drawing`, `female-pose-brushes-figure-drawing`, `koi-fish-tattoo-brushes`, `professional-hair-brushes` (“exact count requires confirmation”), `procreate-mega-bundle-650`, `master-library-2000-brushes`, `master-vault-1000-brushes` (overlap confirmation caveats), `wellness-fitness-planner-goodnotes` (“Files and dates require owner confirmation”). These were the owner-approved transitional compromise from PR #77 (honest copy over silence) and are register item D territory; they are left in place pending your decision — confirm the counts (I can apply them from `scraped/catalog.json` where present, or you confirm on Payhip) or say the word and I will hold these out of the feed too. Left unchanged without your approval.

**D is the cheapest win.** Seven confirmed numbers would immediately lift A, B and the titles at once.

---

## The one decision on your desk

PR #77 (items 1–8) is merged to `main`. The 2026-11-08 follow-up — item 9 (two confirmed counts,
feed regenerated, parser fix), flag H (RAR) and the evidence-file refresh — ships in a separate PR.
Both are reversible: deleting `data/merchant-categories.json` reverts categorisation to Google's
automatic choice on the next build, and `data/merchant-titles.json` can be emptied the same way.

The only open attribution decision is H: re-upload the `pro-sketch-traditional-art-kit` download as
a ZIP on Payhip (recommended, zero copy changes) versus documenting RAR extraction in the install
guide (keeps the file as-is, puts the burden on every buyer).

---

## Honest expectation

The feed is now materially better than it was — but it was never the binding constraint. Seven
unknown counts, one listed download the iPad Files app cannot open as-is (H), six thin listings and
unconfirmed US eligibility matter more than anything else on
this page, and none of them are code.
