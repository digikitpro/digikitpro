# Keyword research — DigiKitPro

**Audit date:** 2026-11-08. **Deliverable 3 of the Merchant Center audit.**

---

## 0. Evidence standard — read before using this document

You asked for search-volume evidence. I am telling you plainly what I have:

| Data type | Available in this audit? | Why |
|---|---|---|
| Exact monthly search volume | **No** | Requires Google Keyword Planner, Search Console, or a paid tool, behind your login. |
| Third-party volume estimates | **No** | Not fetched. Quoting them would mean presenting unsourced numbers as fact. |
| Google Trends relative interest | **No** | Not accessible from this environment. |
| Keyword *existence and commercial intent* | **Qualitative** | Judged from how the products are described, what artists search for, and what the search results pages are shaped like. |

**So: no number in this document is a search volume.** Anything that looks like a ranking is my
judgement, and it is labelled as such. This is the exact gap the previous report filled with
invented confidence.

### Get the real numbers in ~15 minutes

1. **Search Console** (free, already yours): *Performance → Queries*, filter to
   `/products/`. This is the highest-value data you will get, because it shows phrases where your
   pages *already* appear — not phrases we hope they could.
2. **Keyword Planner** (free with a Google Ads account, no spend required): enter the seed phrases
   below, set the location to your real target markets, and export.
3. **Google Trends**: compare "procreate brushes" vs "procreate hair brushes" vs
   "digital planner goodnotes". Relative interest is enough to sequence work.

When you have those three exports, the mapping below becomes a prioritisation instead of a
hypothesis.

---

## 1. How demand actually arrives for this catalogue

Four distinct routes, with different consequences for feed wording:

| Route | What the searcher types | Where it lands | Implication |
|---|---|---|---|
| **Product-specific intent** | "hair stamps for procreate", "anime brushes procreate" | Google Search → product page | Highest conversion. Title must lead with the product type, not the brand. |
| **Technique intent** | "how to draw skin texture procreate" | Guides/blog → product page | Converts later. Needs internal links, not feed titles. |
| **Format intent** | "goodnotes planner pdf", "canva kdp templates" | Google Search / Images | App-name matching is decisive; these buyers do not browse Shopping. |
| **Browse intent** | "procreate brushes" | Shopping tab / Images | Lowest intent per impression, highest volume. Wins on images and counts. |

Merchant Center only touches routes 1, 3 and 4, and route 4 only via Images. That is why
`01-audit-report.md` argues the feed is not the bottleneck.

---

## 2. Keyword clusters mapped to products

Legend: **Intent** B = buying, C = comparison, L = learning. **Fit** = how specifically the product
answers that query, from the product's own record. "Evidence" is qualitative unless stated.

### Cluster 1 — Portrait & skin (highest commercial specificity)

| Phrase | Intent | Fit | Assigned product | Evidence |
|---|---|---|---|---|
| portrait brushes for procreate | B | High | `portrait-mastery-kit-46-brushes` | Category-defined product; 46 confirmed brushes + 4 textures |
| skin texture brushes procreate | B | Very high | `portrait-skin-brushes-procreate` | Product is exactly this; 19 confirmed brushes |
| procreate freckles brush / pore brush | B | Very high | `portrait-skin-brushes-procreate` | Named brushes exist in `included` |
| hair stamps for procreate | B | Very high | `hair-hairstyle-stamp-kit` | 160 confirmed stamps |
| portrait brush bundle | C | High | `ultimate-portrait-mastery-bundle` | Bundle of 4 kits, total count unconfirmed — say "4 kits", not a number |

### Cluster 2 — Watercolour & traditional media

| Phrase | Intent | Fit | Assigned product | Evidence |
|---|---|---|---|---|
| watercolor brushes procreate | B | High | `watercolor-studio-kit-50-brushes`, `organic-watercolor-80-brushes` | 50+ and 80 confirmed counts; split by set size |
| watercolor stamp / splatter brush procreate | B | Medium | `watercolor-studio-kit-50-brushes` | 15 splash stamps confirmed |
| charcoal brushes procreate | B | High | `professional-charcoal-studio` | Compressed/vine/willow tools confirmed |
| pastel brushes procreate | B | Medium | `dreamy-pastel-art-kit` | 10 tools confirmed |
| sketch brushes procreate | B | High | `sketchbook-traditional-media-kit`, `essential-line-art-sketch-kit` | 27 brushes + canvases confirmed for the first |

### Cluster 3 — Line art, ink, anime

| Phrase | Intent | Fit | Assigned product | Evidence |
|---|---|---|---|---|
| anime brushes procreate | B | Very high | `anime-soft-style-brushes-100`, `anime-soft-style-studio-kit` | 100+ confirmed; two overlapping products — pick one as primary |
| line art brushes procreate | B | High | `master-line-art-vault-300` | 300+ confirmed |
| liner brush procreate / inking brushes | B | High | `liner-marker-studio-39-brushes` | 39 confirmed |
| hatching brush procreate | B | Medium | `master-line-art-vault-300` | Hatching tools confirmed |

### Cluster 4 — Effects, patterns, niche

| Phrase | Intent | Fit | Assigned product | Evidence |
|---|---|---|---|---|
| glitter brushes procreate | B | High | `glitter-brushes-sparkle-shine-30` | 30 confirmed |
| pattern brushes procreate | B | High | `brush-palette-bundle-160` | 160 pattern brushes + 12 palettes confirmed |
| smoke brushes procreate | B | Medium | `smoke-brushes-12` | 12 confirmed; very niche |
| tie dye brushes procreate | B | Medium | `tie-dye-brushes-studio` | 21 confirmed |
| procreate color palettes | B | High | `procreate-palettes-bundle-50` | 50 sets / 1,500 swatches confirmed |
| animal fur brushes procreate | B | High | `animal-fur-brushes-2` | 35 confirmed |
| tattoo brushes procreate | B | High | `tattoo-artist-studio-kit-200` | 200+ confirmed |

### Cluster 5 — Planners & templates (different buyer, different surface)

| Phrase | Intent | Fit | Assigned product | Evidence |
|---|---|---|---|---|
| goodnotes planner pdf | B | Medium | `wellness-fitness-planner-goodnotes` | App named in requirements |
| adhd planner 2026 | B | High | `adhd-planner-2026` | 55 pages + 2026 calendar confirmed |
| digital wellness journal | B | Medium | `wellness-journal-2026`, `wellness-journal-365` | Dated vs undated split is the differentiator |
| undated digital planner | B | Medium | `undated-planner-dark-mode` | 2 planners + 1,000 stickers confirmed |
| kdp templates canva | B | Medium | `kdp-templates-bundle-100` | 100+ templates confirmed; licence caveat |

### Cluster 6 — Broad head terms (do not chase from the feed)

"procreate brushes", "digital art brushes", "procreate brush set". Volume is high, intent is
mixed, and competition is dominated by free libraries and large marketplaces. A $5 pack will not
win these on Shopping. Win clusters 1–4 instead and let the head terms arrive via the guides
(technique intent).

---

## 3. Wording rules derived from this research

1. **Lead with the product type**, then the platform: "Portrait Brushes for Procreate: …".
2. **Include the confirmed count** as early as it fits — it is the most persuasive token in the niche
   and the one thing a free library cannot claim. Where the count is unconfirmed, say nothing.
3. **Name the app only when the file requires it** (`.brushset` → Procreate; `.swatches` →
   Procreate; hyperlinked PDF → "for GoodNotes" only where GoodNotes is in the requirements).
4. **Do not stack synonyms.** "Brushes brush set procreate iPad brush" is the failure mode the
   previous advice pushed toward.
5. **Planners are not brushes.** Their queries use app and format words, not style words.

---

## 4. What to do with this after you pull real data

For each product, compare:

- Search Console impressions for the page → does the phrase in this document actually appear?
- Keyword Planner volume → is the cluster worth a title slot at all?
- Merchant Center impressions by `custom_label_0` (class) → did the title change move anything?

Then re-rank Priority A/B/C in `01-audit-report.md` §6 with measurement instead of judgement.
That is the difference between this audit and a keyword list: the list is a hypothesis with a test
attached.
