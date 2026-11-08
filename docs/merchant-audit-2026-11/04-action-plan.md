# Priority action plan

**Ordered by expected impact ÷ risk.** Nothing in this plan has been implemented.

Risk legend: 🟢 reversible, no policy exposure · 🟡 reversible, needs a verification step ·
🔴 needs your decision or your login before anything can be judged.

---

## Step 0 — Before any change: capture the baseline (🔴, 10 minutes, do this first)

You cannot measure an improvement against a metric you never recorded.

1. Merchant Center → **Performance**: set 28 days ending today, filter to **Free listings**,
   **download the CSV**. Note impressions, clicks, CTR per product. This also settles the
   3-vs-0 clicks question — record whether the view says *Free listings* or *All methods*.
2. Search Console → **Performance → Queries**, filter `/products/`, export.
3. Merchant Center → **Products → Needs attention**: screenshot anything listed.
4. Merchant Center → one brush item → read the **Google product category** Google shows.

Step 0 is not optional. Steps 1–3 below are all unmeasurable without it.

---

## Step 1 — Confirm eligibility and shipping in the US (🔴, highest impact, 15 minutes)

**Why first:** if items are ineligible, or missing a shipping service for the US, no copy change
matters. Google states shipping configuration is required for free listings in the US
([13889434](https://support.google.com/merchants/answer/13889434)).

- **Business info → Shipping and returns**: confirm the digital/$0 service exists for the US and
  that the 45 items inherit it.
- If any item shows "Missing shipping service" or "Missing sub-attribute: country", fix it one of
  two ways — **not both**, because feed-level shipping overrides account-level settings:
  1. assign the existing account-level digital service, or
  2. submit shipping per item as **`US:::0 USD`** — the pattern Google documents for
     *"an intangible product such as … digital content, or downloadable software"*
     ([6324484](https://support.google.com/merchants/answer/6324484)).

  In both cases the cost is 0 and **no handling or transit time is submitted**. Inventing "0–1 day
  handling / 0 day transit" is the error to avoid; a 0-cost entry is explicitly sanctioned.
- **Free listings** page: confirm the feature is on and the target countries are the ones you
  actually sell to.

**Exit criterion:** every one of the 45 items has a shipping configuration and a free-listings
status you can name. Send me a screenshot of any diagnostic.

---

## Step 2 — Verify the category override before merging PR #77 (🔴, 10 minutes, gated)

Official position: categories are auto-assigned, and overrides are accepted only for
category-specific attributes, campaign targeting, or alcohol
([6324436](https://support.google.com/merchants/answer/6324436)). PR #77 submits an override for
all 45 items into the `Software` branch — one of the branches that imposes extra required
attributes.

- Merge, wait for one fetch, then check **Needs attention** for new attribute requirements.
- **If new requirements appear → revert** (`data/merchant-categories.json` can be emptied and the
  feed returns to auto-categorisation on the next build). This is a 🟢 rollback of a 🟡 step.
- **If nothing appears and the reported category matches** → keep it.

Honest framing: this is the weakest-justified change in the audit, mine included. It is worth
testing precisely because it is cheap to revert.

---

## Step 3 — Titles (🟡, high impact, low risk)

All 45 proposed titles are in `02-feed-proposed.csv` (50–76 characters, count-bearing where
confirmed).

- Roll out in **Priority A only** first (12 items). A 12-item change is easy to attribute; 45 at
  once is not.
- Titles are feed-only, so landing pages do not drift. Google requires the title to be accurate to
  the page, which it is — same product, same contents.
- **Do not** change `name` in `data/products.json` at the same time; that would move every H1 and
  `<title>` on the site and destroy attribution.

---

## Step 4 — Descriptions, with the AI declaration (🟡, medium impact, policy-sensitive)

Proposed descriptions are in the same CSV. They are machine-written, so:

- They must be published as `structured_description` with
  `digital_source_type=trained_algorithmic_media`, which the repo already supports via
  `data/merchant-ai-provenance.json`.
- Never publish them as plain `description` — that is an undisclosed-AI-content risk.
- Publish in the same Priority A batch as the titles so the two changes are measured together.

---

## Step 5 — Rich product data: the measurable gap (🟢, highest volume of work, fully in-repo)

This is the one item where Google states a target and the catalogue fails it **45 times out of 45**:

- **More than 4 highlights** recommended, **more than 5 details required** for a rich product
  description page ([9479464](https://support.google.com/merchants/answer/9479464)).
- Current state: 3–4 highlights, 4–5 detail rows.
- Rule when expanding ([7052112](https://support.google.com/merchants/answer/7052112)): highlights
  must not repeat `description` or `product_detail` content, and detail values must be confirmed.

Concretely: add 2–3 highlights per item from `included` (real brush names, real components), add
1–2 detail rows (file list, canvas size, palette count), and de-duplicate against the description
so nothing is said twice. This is a code change in `tools/merchant_feed.py` plus per-product review
— reversible, no policy exposure, and it is the change most likely to move listing quality scores.

---

## Step 6 — Fix the thin listings (🟢, needs design work)

6 items have a single image: `master-library-2000-brushes`, `brush-palette-bundle-160`,
`procreate-palettes-bundle-50`, `master-vault-1000-brushes`, `ultimate-fitness-planner`,
`halloween-pumpkin-bundle`. Two of them are flagship bundles.

- Add at least 3 additional images per item: a stroke/feature sample sheet, a contents overview, a
  real usage example inside Procreate or on a painted canvas.
- Images must show the actual product; no fabricated previews of files you do not have.

---

## Step 7 — Close the data gaps that block better copy (🔴, your knowledge only)

9 products cannot state their strongest number because the catalogue marks it unconfirmed. The fix
is one question per product to yourself, then a data edit:

| Product | Missing fact |
|---|---|
| `essential-line-art-sketch-kit` | total brush count |
| `male-pose-brushes-figure-drawing` | stamp count |
| `female-pose-brushes-figure-drawing` | stamp count |
| `koi-fish-tattoo-brushes` | brush count |
| `professional-hair-brushes` | brush count |
| `pro-sketch-traditional-art-kit` | advertised contents |
| `ultimate-portrait-mastery-bundle` | total asset count |
| `anime-soft-style-studio-kit` | bonus set contents |
| `wellness-fitness-planner-goodnotes` | current page/sticker count and dates |

Each confirmed number makes a better title possible and removes a hedge from a description. This
is the highest-leverage unpaid work on the list.

---

## Step 8 — Measurement checkpoint (🔴, calendar)

Come back at **day 28** and **day 90** with the same four exports from Step 0.

Read them in this order:

1. Do impressions exist at all? (If still 0 after eligibility is confirmed, the problem is demand
   or surface, not data — stop optimising copy and move budget of attention to Search/Images.)
2. Impressions by `custom_label_0` — did brush listings move before planner listings?
3. CTR — meaning only once impressions are non-trivial.
4. Sessions on `/products/` pages — separates "Google found us" from "Google converted us".
5. Payhip orders — the only number that pays.

---

## Explicitly not recommended

| Suggestion from the earlier transcript | Why not |
|---|---|
| Bulk attribute rules for `identifier_exists` and category | Bulk rules push one value across a mixed catalogue; both need per-product reasoning. |
| Supplemental data source to override titles | Adds a second source of truth that silently overrides the feed on every fetch. Edit the feed. |
| Creating a shipping service with 0–1 day handling / 0 day transit | The 0 cost is right, the **times** are fabricated for a download. Use the account service, or `US:::0 USD` per item (6324484). |
| Using internal SKUs as MPNs "to be safe" | An MPN must be manufacturer-assigned; if you do assign your own, it is a deliberate decision, not a shortcut. |
| Optimising all 45 at once | Destroys attribution; you will not know which change worked. |

---

## Sequence summary

| Order | Action | Risk | Owner | Impact if it works |
|---|---|---|---|---|
| 0 | Capture baseline exports | 🔴 | you | makes everything else measurable |
| 1 | Confirm US shipping + free-listing eligibility | 🔴 | you | unblocks impressions entirely |
| 2 | Verify or revert the category override | 🟡→🟢 | you + me | prevents new attribute requirements |
| 3 | Titles, Priority A (12 items) | 🟡 | me | better matching on high-intent queries |
| 4 | Descriptions with AI declaration | 🟡 | me | conversion + relevance |
| 5 | Highlights ≥5, details ≥6 for all 45 | 🟢 | me | the one target Google states explicitly |
| 6 | Images for the 6 thin listings | 🟢 | you (assets) | presentation on a visual product |
| 7 | Confirm the 9 counts | 🔴 | you | unlocks stronger titles |
| 8 | 28/90-day read | 🔴 | you | tells us which of the above mattered |
