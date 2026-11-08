# Phase 5 — Organic SEO Strategy (2026-11-08)

**GSC status: not accessible here** — so this is architecture + opportunity, executed blind only until you export 16 months (see `01-visibility-audit.md` §5 and `08-measurement-dashboard.md`). No rankings, positions, or CTRs are claimed.

## What the site already has ([Repo])

18 blog articles (howto schema ×10), guides section, category pages, before/after upgraded homepage, freebie funnel, keyword-mapped article↔product pairs (`PRODUCT-KEYWORD-MAP-2026-10-29.csv`), confirmed 2026-11-08 refresh pass (`230ac66`) that put the plastic-skin problem keyword on the texture article. 104 pages, 101-URL sitemap, IndexNow wired for Bing/Yandex.

## The architecture (grow this, don't improvise it)

```
Home (/) ── /products.html ── PDP ×51
   │             │
   ├── /category/* (7 hubs: portrait, line-art, skin-texture, anime, watercolor, …)
   │        │  each hub = 1 evergreen intro + 2 guides + best sellers
   ├── /guides/* (18 articles — cluster by intent: skin / portrait / install / anime)
   ├── /freebies.html ── email capture ── Essential Line Art / Skin / Bundle
   └── /bundles.html (Ultimate now dialogue for $25 System bundle — see PR #82)
```

**Cannibalisation guard:** each intent has exactly one canonical URL — table in `docs/growth-strategy-2026-11/03-keyword-architecture.csv` ("target_page") + this file's table C in `02-keyword-opportunities.md`. New articles must not re-target `best procreate portrait brushes`; expand related queries instead.

## Internal-link jobs (each page, one job)

- **PDP → 1 contextual guide** (e.g. Skin PDP → "How to Paint Realistic Skin"), 1 collection, 1 adjacent product ("requires" next kit up).
- **Guide → 1 PDP + 1 guide + 1 freebie** with descriptive anchors (never "learn more").
- **Freebie → next paid rung** with honest framing ("if the free set worked for you…").
- **Category hub → top 2 guides** + top 3 PDPs + buy-cluster anchor to bundles.html.

## The striking-distance playbook (once GSC export exists)

1. Pages ranking 5–20 with impressions ≥ some threshold (say >100/mo, owner confirms): refresh date + tighten title/H1 match + add FAQ block → re-index request.
2. Pages with impressions but CTR < 2% on position ≤10: rewrite title links (brand-last, count-forward) — measure 28-day delta.
3. Queries with commercial intent surfacing on blog articles (e.g. "procreate skin brushes"): add a 2-sentence product pointer + link, not a redesign.
4. Coverage report: "Crawled – currently not indexed" on thin seasonal pages → consolidate or noindex deliberately (halloween-pumpkin may qualify).

## Free→paid funnel mechanics (the compounding asset)

Freebie → email (2/mo: one technique post, one offer; ConvertKit/Payhip list) → paid. Every guide closes with one unobtrusive bridge. Goal: the owned list de-risks MC volatility — algorithm changes stop being existential.

## Link & mention earning (organic, no budget)

- 2 brush-roundup listicles accept submissions with demo GIFs (e.g. bebrushes.com, brusher.art — both active 2026) — send 1 GIF per flagship + 1 honest paragraph + link request.
- Pinterest pins (already on every PDP) → visual backlinks + referral.
- Reddit r/ProCreate: answer texture/skin questions with the free guide link (value-first, no product-link spam).
- No mass-directory submissions, no AI article farms (they de-index in 2026).

## Sequence with the 90-day plan

Days 16–30 = landing pages + internal links (Phase 4 P1, this file's architecture); Days 31–60 = publish strategy articles 6–8 with Pinterest; Days 61–90 = expand what GSC proves. Execution and owners: see `07-90-day-traffic-plan.md`.
