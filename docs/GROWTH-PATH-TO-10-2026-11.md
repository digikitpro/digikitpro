# The honest path from 6.5/10 to 10/10 (2026-11-08)

Your scorecard, what moved today, and — plainly — what no PR can move. The rule of this doc: **verified work vs owner-only reality.** No invented lifts are promised.

## What changed in code this PR

1. **Explicit compatibility line** on every non-guide PDP, sitting in the trust list under the buy panel: "Procreate on iPad only — not Photoshop, Clip Studio or Android." The #1 source of "doesn't work" disappointment, stated before checkout instead of after.
2. **Founding reviews machinery** — `reviews` in `data/products.json` now renders (a) a "What buyers say" section after features on the PDP, and (b) `Review` JSON-LD inside the Product node. Renders **nothing** until real quotes exist: zero fabrication risk by construction, zero empty boxes in the UI today. See [owner-kits/founding-reviews.md](owner-kits/founding-reviews.md) for collection.
3. **CSS** for the reviews grid added (token-based, matches existing surfaces/gold).

## What is still structurally holding the score (owner-side; no PR can fix)

| Gap | Score impact | What it needs | Rough effort |
|---|---|---|---|
| MC free-listings eligibility unknown (US shipping settings unconfigured/unverified) | Blocks visibility dimension entirely | You: configure US shipping (digital goods) + refund URL in MC + confirm Free listings card, then CTR export | ~30–45 min |
| Zero reviews | Trust dimension | You: 3–5 consenting quotes via the kit above; paste into catalog; rebuild | ~30–45 min |
| No anchor product ($19–29 ladder rung) | Conversion/economics | PR #82 merge decision (Complete Portrait System $25) — then Payhip listing + cover + wiring PR | ~1–2 h |
| Single-image listings (6 SKUs) | Perceived quality | You: real preview renders/artwork exported from your own files or with consent — I cannot conjure accurate brush art | asset request to yourself |
| Buyer-visible "awaiting confirmation" caveats (9 items) | Credibility | You: confirm counts (4 of them verified 2026-11-08 — apply them), or accept hold | ~15 min |
| Distribution beyond Payhip + organic | Distribution dimension | You: decide on Etsy/Gumroad/Creative Market expansion (fees & counters trade-off) — separate business decision | decision + setup |
| Benchmarks: zero metrics from Google/MC/Shopify-class reporting | Measurement | You: file GSC 16-month + MC 28-day exports (intake in [growth-strategy-2026-11/baseline-2026-11.md](growth-strategy-2026-11/baseline-2026-11.md)) | ~20 min |

## Definition of "10/10" that is fair to everyone

- **Every listing eligible and measured**: shipping configured, free listings ON, zero unexplained flags, monthly KPI cadence producing actual deltas.
- **Social proof present and real**: ≥3 genuine founding quotes visible on the top PDPs + at least one marketplace or platform-verified signal if you choose expansion.
- **A complete ladder**: free → $5–8 kits → $19 Masterclass → $25 System Bundle → $97 efforts, all in stock, all with verified contents statements — i.e. the full Intent Flow Google can match against.
- **Conversion loop closed**: Payhip conversion rate tracked, ≥1 monthly iteration shipped, free→email→paid sequence live.
- **Zero unfixed trust leaks**: no ∃-count caveats, every product ≥4 images, every file format story crystal clear (e.g. .rar pro-sketch resolved via ZIP re-upload).

None of that is imaginary effort — it's a 2–4 week owner-side sprint plus the work already merged. What I can NOT honestly grant you: instant rankings, instant sales, or a number any higher than the evidence supports. What I can guarantee: as soon as the three owner actions land (shipping/free-listings ON, reviews pasted, exports filed), this codebase will surface them correctly everywhere Google and buyers look.
