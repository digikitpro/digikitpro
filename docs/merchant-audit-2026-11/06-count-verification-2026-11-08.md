# Count & claim verification — 2026-11-08 (register item D)

**Scope:** the products carrying unconfirmed brush/stamp/file claims in `data/products.json`, flagged in `00-HIGH-status.md` item D and visible to Google as "confirmation"-caveat highlights.
**Sources:** `scraped/catalog.json` (the scraped Payhip listings, captured 2026-10; **not live re-verified today** — Payhip is not reachable from this environment), `data/products.json`. Owner confirmation on the live listings remains the final authority.
**Method:** each product's listing text was read for an explicit stated count. "Verified" below means *the listing itself states the number* — not that we inspected files. No counts were edited in this pass; copy changes await owner approval (see recommendations).

## Verdict table

| Product | Payhip (`scraped/catalog.json`) | Listing states | Verifiable? | Note |
|---|---|---|---|---|
| `procreate-mega-bundle-650` ($20) | `anHCt` | **650+ brushes** (title + desc), **24 brush sets** | ✅ listing-stated | Caveat remaining is *overlap* with other bundles, not the 650+ figure. Overlap stays unknown unless owner confirms contents; do not publish overlap claims. |
| `master-library-2000-brushes` ($19) | `G2N8m` | **2,000+ brushes** (title), **14 ZIP files** | ✅ listing-stated | 14 files ≈ 14 component kits; consistent with the 2,000+ claim. |
| `master-vault-1000-brushes` ($15) | `VtnCF` | **1,000+ brushes** (title), **4 ZIP files**, "total value … over $1,600" | ✅ listing-stated | Value-anchor is the listing's own claim; reuse verbatim or delete. |
| `brush-palette-bundle-160` ($5) | `8lF29` | **160 pattern brushes + 12 curated palettes**, 12 files, "filled + transparent versions" | ✅ listing-stated | The current hedge ("counting method unconfirmed") is outdated — the listing is explicit. |
| `male-pose-brushes-figure-drawing` ($5) | `foZi0` | **No count stated anywhere**; ZIP 13MB | ❌ cannot verify | Needs owner to count stamps in the file or amend the listing with the real number. 2 caveat strings exist in `features`. |
| `female-pose-brushes-figure-drawing` ($5) | `8o651` | **No count stated**; ZIP 11MB | ❌ cannot verify | Same. |
| `koi-fish-tattoo-brushes` ($9) | `KM1a5` | **No count stated; `files: []`** — delivery file unverifiable | ❌ cannot verify **+ delivery risk** | Same empty-file signature as `pro-sketch-traditional-art-kit` (register H). Recommend owner check the Payhip delivery file too. |
| `professional-hair-brushes` ($5) | `Dqr26` | **No count stated**; ZIP 14MB | ❌ cannot verify | Listing enumerates "Hair Stamps" + "Textured Strand Brushes" without numbers. |
| `wellness-fitness-planner-goodnotes` ($5) | `Q2UdG` | "**900+ Hyperlinked Planner Pages**", "**2022 Digital Planner Stickers**" — and the listing text contains **the owner's own unfinished edit-checklist** ("Update the year - Change '2022' to '2026'…", "Consider pricing strategy") visible to buyers | ⚠️ count partially stated; **listing leaks internal notes** | Bigger issue than a number: buyers currently see the draft checklist. Owner must rewrite the listing body (and decide 2022→2026/undated) regardless of this audit. |

`pro-sketch-traditional-art-kit` (register H) is already out of the feed (PR #81) and excluded from this table.

## What this means for items A/B/D (highlights, detail rows, titles)

- The four ✅ products can be truthfully rewritten today **if you approve** the copy change — e.g. drop "requires confirmation" caveats, state 650+ / 2,000+ / 1,000+ / 160+12 as facts sourced to the listings, and QA will then enforce "no caveat reintroduced".
- The four ❌ products stay exactly as they are (honest caveats) until you supply the numbers — I will not invent them and cannot derive them from file sizes.
- `wellness-fitness-planner-goodnotes`: regardless of counts, the listing's leaked checklist needs a rewrite on Payhip (you), then the product page/PDP technical row can be aligned (I can do this after).

## Recommended approval sequence

1. Approve "✅ products: apply listing-stated numbers" → one small PR (feed/titles/copy regenerated + QA) — riders: keep the bundle-overlap caveat **out** of buyer copy but out of Google highlights too (replace overlap caveats with the verified 650+/2,000+/1,000+ facts, which are non-overlapping statements).
2. Owner supplies counts for male/female-pose, koi, hair (or edits those Payhip listings to state them — then we read them from a re-scrape).
3. Owner rewrites the wellness-planner listing body (or tells me it's already fixed and I re-scrape).
4. Owner checks `koi-fish-tattoo-brushes` delivery file (empty `files` list in the scrape).

## Not done in this pass (deliberately)

- No changes to `products.json`, feed input data, pages or feed XML — per "no live changes without approval".
- The nine buyer-visible caveat highlights flagged in PR #81 stay in place until the copy change above is approved.
- No live re-scrape possible from this sandbox; evidence is the 2026-10 scrape.
