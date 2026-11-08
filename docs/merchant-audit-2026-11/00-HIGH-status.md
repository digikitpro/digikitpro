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

Feed: 45 items, 147 KB. All suites pass — 15 merchant tests, 1,229 editorial checks, 115 verify checks.

---

## Still High, and genuinely blocked

| # | Issue | Count | Why I can't fix it | What unblocks it |
|---|---|---|---|---|
| A | Highlights below Google's bar | **9** items | The record states fewer than 4 facts; padding means inventing | Add a fact to `features` |
| B | Detail rows below Google's bar | **25** items | Same — no sixth stated spec exists | Add a fact to `technical` |
| C | Single-image listings | **6** items (incl. `master-library-2000-brushes`, `brush-palette-bundle-160`) | I cannot fabricate product previews | Real images |
| D | Unconfirmed brush/stamp counts | **9** products | Only you know the numbers; your own page says they disagree | Confirm each count |
| E | US shipping / eligibility | all 45 | Needs your Merchant Center login | Confirm the digital service or `US:::0 USD` |
| F | Category override may impose `Software` field requirements | all 45 | Google only *accepts* overrides in 3 cases; mine is accuracy | One fetch, then keep or revert |
| G | Baseline never captured | — | No access to impressions/clicks | Export 28-day data before judging |

**D is the cheapest win.** Nine confirmed numbers would immediately lift A, B and the titles at once.

---

## The one decision on your desk

PR #77 is open and now contains items 1–8. It is reversible: deleting
`data/merchant-categories.json` reverts categorisation to Google's automatic choice on the next
build, and `data/merchant-titles.json` can be emptied the same way.

Merge order that keeps attribution: **merge, fetch once, read back one category (F), then compare
28 days.** If you would rather test titles before categories, say so and I will split the PR.

---

## Honest expectation

The feed is now materially better than it was — but it was never the binding constraint. Nine
unknown counts, six thin listings and unconfirmed US eligibility matter more than anything else on
this page, and none of them are code.
