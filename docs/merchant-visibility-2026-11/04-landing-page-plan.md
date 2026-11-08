# Phase 4 — Product Landing Page (PDP) Improvement Plan (2026-11-08)

Audited via live fetch (homepage/PDPs render, `robots.txt` clean, 104 pages pass the site's 3,207 SEO invariants; 115/115 verify checks; 44 PDPs' Payhip links + price/canonical/image parity evidenced in `docs/merchant-audit-2026-11/05-landing-evidence.csv`). PDP = 44 feed items' destinations (live pages); pro-sketch PDP exists but is out of the feed.

## Scorecard (template level — applies to all PDPs)

| Check | Verdict | Evidence / gap |
|---|---|---|
| Title tag / SEO title | ✅ pass | `seoTitle` enforced; `qa_seo` PASS |
| Meta description | ✅ pass | enforced length + uniqueness |
| H1 = product name (single) | ✅ pass | `pdpH1` used |
| Price = feed price = visible price | ✅ pass | parity enforced; 44/44 link checks |
| Images: full-bleed covers, srcset, lazy, alt text | ✅ pass (QA) / ⚠️ cover *quality* | artwork strength unknown from data; 8 items ≤1 image? no — all items have ≥2 images except flagged (C: 6 items single-image? register says **6 single-image items**; those are pro-sketch (held) + others — owner to supply real previews |
| Structured data (Product + Offer + Breadcrumb + FAQPage) | ✅ structurally valid | rich-result eligibility = GSC, not testable here |
| Compatibility statement | ⚠️ weak | trust bridge says Procreate/iPad required — but a 2-line **explicit "works on iPad + Procreate only; NOT Photoshop/Clip Studio"** box near the CTA is absent on some PDPs; top driver of "doesn't work" reviews |
| Download format & size | ✅ present | `.brushset`, ZIP sizes stated; install guide linked |
| "How to install" 3-liner on PDP | ❌ missing site-wide | install article exists but PDPs don't embed the steps; adding cuts pre-sale friction (competitor support threads agree) |
| Internal links (related article + collection + freebie) | ✅ partial | guides linked; freebie ladder not consistent per PDP |
| Licence line (personal vs commercial) | ⚠️ generic | licence_line exists near CTA; per-product commercial tier unstated — True Grit leads here |
| Reviews / social proof | ❌ missing | zero on-site reviews vs Etsy competitors' visible counters |
| Availability ("in stock") + Schema availability | ✅ | `schema.org/InStock` |
| Mobile usability | ✅ structural (responsive) / ⚠️ not device-tested | run PageSpeed/Chrome DevTools once |
| Speed / CWV | ❓ unknown (no field data) | hero WebP preload exists on PDPs; run PSI on 5 templates: home, products.html, category, PDP, article |
| Buyer friction: freebie next-step for free items | ✅ present on free PDPs | |

## Priority actions (template fixes — one PR each or batched)

**P1 — done (this branch's PR, 2026-11-08)**

1. ~~Compatibility statement~~ → every non-guide PDP now carries **"Procreate on iPad only — not Photoshop, Clip Studio or Android"** in the trust list directly under the buy panel (verification line stays in requirements). Full compatibility+licence box in the ideal wording remains optional polish.
2. ~~Install help strip~~ → already present via `install_steps()` (format-aware: PDF/.brushset/.swatches) — verified present on all PDPs; no re-add needed.
3. **Reviews block** → machinery merged: PDP renders "What buyers say" + Product JSON-LD `review` only when real quotes exist in `data/products.json` (see [../owner-kits/founding-reviews.md](../owner-kits/founding-reviews.md)). Content pending owner-collected founding quotes — **never fabricated**.

**P2 — next 30 days**

4. Freebie ladder strip on top-5 PDPs ("new here? start with the free liner set" — check exists freebies flow).
5. Related-article slot consistent across PDPs (currently 0–1; make it exactly 1 contextual guide + 1 collection).
6. Alt-text re-audit on the 8 P2 low-highlight SKUs' galleries (brush sample shots need descriptive alts like "portrait skin texture brush stroke pores freckles").

**P3 — hygiene**

7. Date/refresh note on PDPs whose counts were confirmed 2026-11-08 (Skin, Essential Line Art, Bundle) — subtle credibility line.
8. Kill any lingering internal-audit caveat copy that survived rebuilds (QA bans; verify 0 occurrences remain — currently true).

## Feed ↔ PDP parity rule (must hold forever)

Any PDP change to **price, title claims, counts, compatibility, licence** must regenerate the feed (`tools/build.py`) — the two are generated from one source (`data/products.json`) precisely so they cannot drift; `qa_merchant_feed` enforces description/hash sync and `verify.py` checks price parity. Never hand-edit `google-merchant-feed.xml`; edit catalog + rebuild.

## Explicitly not done / owner-only

Real image refreshes (C: 6 single-image items — can't fabricate product art), review collection campaign (needs your proof of purchase: email 10 recent buyers?), PageSpeed/CrUX field data, mobile device pass, MC destination links test after next fetch.
