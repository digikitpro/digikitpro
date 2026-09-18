# Homepage exact reorder + UX upgrade — 2026-09-18

Owner brief: reorganize and refine the **existing** homepage around an exact
section sequence. No URL migration, no palette change, no new products, no
fabricated proof. Everything below is generated from the same catalog data
(`data/products.json`, `data/discovery.json`) — **neither file was edited**,
so a daily Payhip sync keeps working unchanged.

## What changed (homepage only)

**New section order** (was: hero → trust band → popular(7) → craft → bundles →
master library → free → ebooks → before/after → why → articles → email):

1. **Hero** — same headline/CTAs/trust row; right side is now ONE large
   finished portrait (was a 3-cover stack) that links to the skin-brushes PDP.
2. **Before/After proof** — moved from #9 to directly under the hero; added
   the "skin texture → pores → freckles → hair → final polish" step chips.
3. **Start With What You Actually Need** — the old "Popular" section cut from
   7 items (spotlight + 6) to 4 focused kits (skin, mastery, line art,
   watercolor), each with View Product **and** Payhip Buy Now (new `dual_buy`
   option on the shared product-card component; off everywhere else).
4. **What Do You Create?** — workflow cards now carry one real artwork each
   (`core.CRAFT_ART` map, same category URLs and counts).
5. **Try DigiKitPro Before You Buy** — Starter Guide leads the three $0 kits;
   all four buttons go straight to Payhip.
6. **From First Portrait to Finished Portrait** — NEW: the journey
   $0 guide → $5 skin → $8 kit → $15 bundle → $19 Masterclass. Horizontal on
   desktop, vertical timeline on mobile. Replaces the two-card ebook duo.
7. **Want More Than One Kit?** — the bundle ladder, repositioned after the
   journey, with copy that explains *which rung to pick* instead of "more is
   better".
8. **One Library. Multiple Workflows. Less Tool Hunting.** — Master Library
   feature: nine workflows as scannable chips; secondary CTA is Compare
   Bundles. (`flagship_band(home=True)`; the thank-you/guide pages keep the
   old variant byte-for-byte.)
9. **Tools That Respect Your Craft** — same four factual claims + quiet icons.
10. **Made for Real Artwork** — NEW honest placeholder: three empty, clearly
    marked slots + share invitation. No quotes/names/artwork — `verify.py`'s
    honesty guard still applies.
11. **Learn Procreate. Create Better.** — the same three guides, repinned to
    beginners → line art → anime.
12. **Get the Free Procreate Starter Pack** — unchanged email CTA.
13. Footer — unchanged.

Removed from the homepage: the full-width trust band (its claims live on in
the hero trust row, the Why section, and untouched on `products.html`), the
best-seller spotlight band, and the ebook duo + Look-Inside strip (absorbed
by the free row and the journey). All products, PDPs, Payhip links, Pinterest
Save buttons, Instagram/Pinterest destinations, JSON-LD and the single-H1
outline are preserved.

## Verify

`tools/verify.py` re-pinned the two homepage-IA checks to the new order
(`results → popular → craft → free → journey → bundles → master-library →
why → proof → articles → newsletter`, closing `proof → articles → email`).
Count unchanged: **ALL 82 CHECKS PASSED** after a full `tools/build.py`.

## Rebuild

    python3 tools/build.py && python3 tools/verify.py
