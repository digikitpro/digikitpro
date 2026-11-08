# Proposal — "The Complete Portrait System" bundle (NOT IMPLEMENTED — owner decision first)

**Date:** 2026-11-08 · **Status:** proposal for review; nothing in the repo or on Payhip is changed by this document. Build-ready spec included so execution is mechanical once approved.

## Why this bundle (evidence, not vibes)

- Catalogue anchor: the **Ultimate Portrait Mastery Bundle** (4 kits / 252+ assets, **$15**, featured) proves bundle demand in this exact niche on this exact store.
- Competitor ladder (all [Verified-public], 2026-11-08): Lisa Glanz brush+tutorial sets **$16–21** with visible review flow; RetroSupply Complete Collection **$197**; ArtbyKimmyw portrait bundle **$50** with **1,106 sales** on Creative Market; ArtworkbyGabrielle portrait brushes **$4.80** on Etsy (8.8k-sale shop). Every serious portrait competitor bundles *education + tools*, not tools alone.
- DigiKitPro's gap: the **Masterclass eBook ($19)** — its highest-consideration portrait asset — is excluded from the Google feed (Guides & eBooks policy) and barely merchandised. It converts informational traffic the brushes can't.

## Component duplication check

| Design | Components | À la carte | Suggested System price | Save | Duplicate vs $15 Ultimate bundle? |
|---|---|---|---|---|---|
| A — tools+education, maximal | Mastery Kit ($8) + Skin Kit ($5) + Masterclass eBook ($19) | $32 | $22 | $10 (31%) | Skin's 19 brushes duplicate one kit of Ultimate — disclosed, but tool-heavy |
| **A2 — whole portrait catalogue + masterclass (RECOMMENDED)** | **Ultimate Portrait Mastery Bundle ($15) + Masterclass eBook ($19)** | **$34** | **$25** | **$9 (26%)** | **Zero duplication — literally everything portrait, once** |

**Recommendation: A2.** Cleanest story ("every portrait kit we make + the full guided masterclass, one download"), no "why is Skin in two bundles" confusion, protects the $15 Ultimate as the tools-only rung, and the $25 price sits above every current catalogue item without new art beyond a cover.

Rejected: A (duplication + weaker story); bundling anything with Pro-sketch (H unresolved); bundling free products (devalues the freebie ladder); fake anchor pricing ("was $34" wording is banned — state plain arithmetic instead).

## What the owner must decide/do (I cannot)

1. Pick A2 (recommended) or A.
2. Create the Payhip product: deliverable = the **Ultimate bundle ZIP + Masterclass PDF** (A2). Set price ($25 suggested) and description — I can draft the copy for approval.
3. Cover art: new composite cover (recommend: masterclass cover art + "includes the $15 kit" ribbon), **not** fabricated artwork presented as real painting; reuse of existing component covers with new layout is the honest cheap route.
4. Commercial-use wording must match the most restrictive component.

## Apply-ready spec (A2) — after the listing exists

**products.json entry** (add to array; `id` = Payhip product id, `payhipUrl` = real listing URL — **owner supplies both**):

```json
{
  "id": "OWNER_PAYHIP_ID",
  "name": "The Complete Portrait System: 252+ Brushes + Portrait Masterclass",
  "slug": "complete-portrait-system",
  "category": "Bundles",
  "price": 25.0, "priceText": "$25.00", "currency": "USD", "free": false,
  "badge": "Bundle", "featured": 2,
  "assets": "252+ assets across 4 kits + 107-page Masterclass eBook",
  "short": "Every portrait kit we make plus the full guided Masterclass — one download, $25 (à la carte $34).",
  "tags": ["bundle", "portrait", "masterclass", "ebook", "skin", "hair", "line art", "workflow", "value"],
  "payhipUrl": "OWNER_PAYHIP_URL",
  "bundleContents": [
    {"name": "Ultimate Portrait Mastery Bundle (4 kits)", "count": "252+ assets"},
    {"name": "The Complete Procreate Portrait Masterclass (eBook)", "count": "107 pages · 15 chapters"}
  ]
}
```

**Remaining wiring** (I do this after step 1–3 above, in its own PR): merchant-categories.json row (reuse the `Bundles` class/node used by the Ultimate bundle — I'll confirm the exact node from `data/merchant-categories.json` rather than guess); image assets + size table; `bundles.html` third row with the honest $15/$19→$25 maths; PDP from the existing bundle template (no code changes); feed inclusion (paid, non-book → eligible); QA × 6 suites; IndexNow ping.

**Success metric (day 30):** bundle orders ≥ 5 or CTR on its MC entry ≥ store median; otherwise re-price/reposition rather than discount-spam.

## What this proposal deliberately avoids

No invented Payhip URL, no fake product in the catalog, no fabricated sales forecasts, no new SKU before the delivery file exists — implementation happens only against a real listing, verified price and owner-approved copy.
