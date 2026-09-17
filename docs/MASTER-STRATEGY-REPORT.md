# DigiKitPro — Master Strategy Report

**Date:** 2026-09-17  
**Scope:** Website conversion · Instagram · Pinterest · Masterclass · Artist Radar · Experiments  
**Sources:** Live site `https://digikitpro.shop/`, repo generators, `data/products.json` (51 products), existing `docs/AUDIT-AND-PLAN.md` + `docs/PINTEREST-30-DAY-PLAN.md`, 5 real Masterclass interior pages supplied by owner.

**Honesty rules (enforced throughout):** no invented reviews, no fake traffic numbers, no fabricated interior pages, no price hikes as the primary fix, no auto-email outreach.

---

## Positioning lock (use everywhere)

| Stop saying | Start saying |
|---|---|
| Lots of brushes for cheap | Procreate tools organized around your creative workflow |
| 2,000+ brushes mega dump | SKETCH → INK → BLEND → HAIR → DETAIL → TEXTURE → FINISH |
| Cheap option | Affordable · useful · organized · educational · trustworthy |

**Product ladder (customer journey spine):**

```
FREE  →  SPECIALIST ($4–$7)  →  WORKFLOW KIT ($8–$10)  →  BUNDLE ($15–$20)  →  MASTER LIBRARY ($19)  →  MASTERCLASS ($19 education)
```

Masterclass is the **education layer**, not “another pack.” Never upsell Master Library against it with a +$0 delta.

---

# A. WEBSITE

## A1. What is already strong (do not rebuild)

Verified on live site + repo:

1. **Workflow-aware homepage IA** — hero → craft grid → free → Learn (Starter Guide + Masterclass) → before/after → starting points → bundle ladder → Master Library → why → articles → email.
2. **Product hierarchy in `data/discovery.json`** — free / entry / bundle / flagship / education.
3. **Brush Finder architecture** (`tools/pages_finder.py`) + analytics events + thank-you page.
4. **Pinterest plumbing** — domain claim, Save buttons, Rich Pin meta, catalog feeds, 30-day pin plan.
5. **18 technique articles + 5 commercial buyer guides + 10 category pages.**
6. **Honest social-proof policy** — empty until real; `verify.py` blocks invented quotes.
7. **Premium dark/gold design** — preserve.

## A2. Current weaknesses (ranked by revenue impact)

| # | Weakness | Evidence | Impact |
|---|---|---|---|
| **W1** | **Masterclass PDP described install as `.brushset`** | Live page said “the .brushset file arrives by email” on a PDF eBook | Trust destroyer at the exact moment of purchase |
| **W2** | **Masterclass licence line said “brush files”** | Same PDP | Format confusion |
| **W3** | **Masterclass upgraded to Master Library at +$0** | Education tier got brush-library upgrade panel | Confuses education vs tools ladder |
| **W4** | **Masterclass gallery = cover only** | `images.gallery: []` — no interior pages on PDP | Buyer cannot “see what I’m getting” |
| **W5** | **Instagram not wired on site** | `SOCIAL["Instagram"]` was empty → no footer/schema `sameAs` | Missed trust + discovery loop |
| **W6** | **No real social proof slot populated** | Correct empty state, but zero collection system running | Silent conversion tax |
| **W7** | **Email = FormSubmit only, no drip** | List grows; no sequence | Free → paid ladder leaks |
| **W8** | **Hero CTA still “Browse kits” → full catalog** | Highest intent sent into 51-card grid | Discovery friction |
| **W9** | **Lifestyle products mixed in catalog** | Owner accepted risk; still dilutes Procreate promise | Positioning tax (measure, don’t delete yet) |
| **W10** | **`find-my-brushes.html` may be missing from this checkout artifact** | Generator exists; page not always present until full build | Discovery path incomplete until rebuild/deploy |

## A3. Fixes already applied this session

| Fix | File | Result |
|---|---|---|
| Format-aware `install_steps(p)` | `tools/core.py` | Masterclass → “How to use it” + PDF path; brushes keep `.brushset` path |
| Format-aware `licence_line(p)` | `tools/core.py` | eBook vs brush wording |
| Skip upgrade panel on `education` tier | `tools/core.py` | No Master Library pitch on Masterclass |
| Wire Instagram profile | `tools/core.py` | Footer + schema `sameAs` → `instagram.com/digikitprostudio` |
| Product pages rebuilt | `products/*/index.html` | Live HTML matches generator |

## A4. Highest-impact next fixes (priority order)

### P0 — ship this week (conversion blockers)

1. **Add the 5 real Masterclass interiors to the PDP gallery**  
   - Path: `assets/products/procreate-portrait-masterclass-ebook/interior-01.webp` … `interior-05.webp`  
   - Wire via `images.gallery[]` in `data/products.json` (Payhip sync must not wipe hand gallery — keep interiors outside auto-sync overwrite, or re-apply in a post-sync step).  
   - Section title on PDP: **“Inside the Masterclass”** (not “install gallery”).  
   - Measure: `scroll_depth` 50/90 on Masterclass + `product_buy_click` rate.

2. **Full site rebuild + deploy** so Instagram footer, eBook install copy, and finder page are live everywhere.

3. **Hero secondary CTA**  
   - Primary: `Find My Brushes` → `find-my-brushes.html`  
   - Secondary: `Browse kits`  
   - Measure: `brush_finder_started` vs old hero click-through.

4. **Masterclass cross-sell on portrait path only**  
   - After buy panel on: Skin Brushes, Portrait Mastery Kit, Portrait Bundle, free Starter Guide.  
   - Copy: “Learn the workflow these brushes sit inside — 15 chapters, PDF.”  
   - Link interiors 1-thumbnail (Contents or Ch.07).  
   - Do **not** show Master Library upgrade on education pages (already fixed).

### P1 — next 2 weeks

5. **Social proof collection system (no fakes)**  
   - Google Form: artwork + permission + product used + optional quote.  
   - Store approved rows in `data/artists.json` (render only when non-empty).  
   - Homepage band + PDP strip when ≥3 approved.

6. **ESP switch (MailerLite/Brevo free tier)**  
   - One-line `EMAIL_ENDPOINT` swap already designed.  
   - 5-email sequence already written in `AUDIT-AND-PLAN.md` Part 9.  
   - Tags from existing `source` + `lead_magnet` fields.

7. **PDP media standard for top 8 revenue kits**  
   - For each: stroke swatch → application close-up → finished piece (or before/after).  
   - Priority: Skin, Portrait Mastery, Line Art, Hair, Watercolor, Anime Soft-Style, Portrait Bundle, Master Library.

8. **GA4 dashboard (owner, 30 min)**  
   - Custom report: `product_view` → `outbound_payhip_click` by slug.  
   - Baseline week 0 before any further homepage experiment.

### P2 — later

9. Bundle `bundleContents` for remaining 5 bundles.  
10. Commercial SEO pages for hair / skin (already have skin article).  
11. Lifestyle separation revisit after 30 days of GA4 (owner decision #2 in audit).

## A5. Homepage section target (vs current)

| # | Target | Current status |
|---|---|---|
| 1 | HERO | ✅ |
| 2 | WHAT DO YOU CREATE? | ✅ |
| 3 | FREE START | ✅ |
| 4 | SEE THE DIFFERENCE | ✅ (demo artwork; swap for real client BA when available) |
| 5 | POPULAR / RECOMMENDED | ✅ |
| 6 | PRODUCT LADDER | ✅ (bundles) |
| 7 | MASTER LIBRARY | ✅ |
| 8 | LEARN | ✅ (earlier than brief — better for education-first) |
| 9 | CUSTOMER ARTWORK | ❌ empty by design until real |
| 10 | EMAIL CAPTURE | ✅ |

**Do not** re-shuffle homepage again without GA4 proof. Current order already routes intent before catalog.

---

# B. INSTAGRAM

**Account:** https://www.instagram.com/digikitprostudio  
**Role:** TRUST + EDUCATION + DISCOVERY (not a product catalog)

## B1. Audit limits

Instagram returns HTTP 403 to automated fetch. Audit is therefore **structural** (repo wiring + recommended system), not a live post-by-post scrape. Owner should paste: current bio, link-in-bio tool, last 12 posts mix, Reels vs static ratio.

## B2. Strengths to build on

- Brand handle matches email/domain (`digikitprostudio`).
- Product photography and Masterclass page design are already premium enough to screenshot.
- Site now links Instagram in footer + schema (this session).

## B3. Weaknesses to assume until proven otherwise (new brand pattern)

| Issue | Fix |
|---|---|
| Bio sounds like a shop dump | Workflow + free + education |
| Grid is cover-art heavy | 60% education / 25% process / 15% product |
| No pinned “start here” | 3 highlights + 3 pinned posts |
| Link goes only to homepage | Link-in-bio with 6 destinations |
| No Masterclass interior proof | Rotate the 5 real pages |

## B4. Profile (paste-ready)

**Name:** `DigiKitPro | Procreate Workflow Tools`  
**Bio (≤150 chars):**
```
Procreate tools organized around your workflow.
SKETCH → INK → BLEND → DETAIL → FINISH
Free brushes + Portrait Masterclass
```
**Link:** Linktree / Beacons / native multi-link with:
1. Free Fine Liner Set  
2. Free Portrait Starter Guide  
3. Portrait Skin Brushes  
4. Portrait Masterclass  
5. Find My Brushes  
6. Full shop  

**Highlights (order):** Start Free · Skin · Hair · Line Art · Masterclass · Before/After  

**Pinned posts:** (1) Free starter carousel, (2) Masterclass Contents page, (3) Skin before/after.

## B5. Content pillars (weekly mix of 5 posts + 3–5 Stories)

| Pillar | % | Format | Example hooks |
|---|---|---|---|
| 1 Education | 30% | Carousel / Reel | “Light is design. Values are your plan.” |
| 2 Before/After | 15% | Reel / slider | Flat skin → textured finish |
| 3 Masterclass interiors | 15% | Carousel of REAL pages | Ch.07 detail process |
| 4 Product demo | 15% | Reel PROBLEM→PROCESS→RESULT→TOOL | “Stop plastic skin” → Skin Brushes |
| 5 Artist problems | 15% | Static + caption | “3 mistakes beginners make with brushes” |
| 6 Free entry | 10% | Static / Story | Free liner / free eBook |

**Never** three product posts in a row.

## B6. Posting system (sustainable)

| Cadence | What |
|---|---|
| **3 feed posts / week** | Mon education · Wed process/BA · Fri Masterclass or free |
| **2–4 Reels / week** | 7–15s screen record; text hook first 1s; no voice required |
| **Daily Stories** | 1 tip + 1 poll + 1 link sticker (free or PDP) |
| **Batch block** | 90 min Sunday: 6 carousels + 4 Reel clips from one portrait session |

## B7. Product promotion system (not “buy this”)

**Formula on every product post:**

```
HOOK (problem) → 1–3 process frames → RESULT → TOOL (one product) → soft CTA
```

**CTA ladder by coldness:**

| Audience temperature | CTA |
|---|---|
| Cold | “Save this” / “Free pack in bio” |
| Warm | “Full breakdown on site” |
| Hot | “Link in bio — Portrait Skin Brushes $5” |

**Masterclass posts:** show real interior → “107 pages · 15 chapters · PDF · $19” → link Masterclass PDP (not homepage).

## B8. Caption template

```
[Hook — 1 line problem]

[3–5 lines teaching — one actionable tip]

Workflow: Sketch → Ink → Blend → Detail → Finish

[Product only if earned]
Tool used: [name] · [price if shop post]

Save for your next portrait.
Free starter pack → link in bio
```

Hashtags: 3–8 max, niche (`#procreatebrushes #procreateportrait #digitalpainting #ipadart`).

## B9. Metrics (weekly)

Reach · Saves · Shares · Profile visits · Link clicks · Follows from content · Saves on Masterclass posts · Site sessions from IG (GA4).

**Success ≠ followers.** Success = profile visits → free download → email → PDP.

---

# C. PINTEREST

**Account:** https://www.pinterest.com/DigiKitProStudio  
**Role:** SEARCH DISCOVERY + EVERGREEN TRAFFIC + PRODUCT DISCOVERY

## C1. Strengths (already in repo)

- Domain claim tag live on all pages.
- Save buttons + `data-pin-*` on product imagery.
- Product Rich Pins meta.
- `pinterest-feed.csv` / `.xml` catalog feeds.
- Full **30-day plan** in `docs/PINTEREST-30-DAY-PLAN.md` (3 pins/day, 5 boards, Idea Pins).
- Buyer guides + technique articles as pin destinations (not only homepage).

## C2. Weaknesses / owner actions still required

| Gap | Action |
|---|---|
| Claim may not be confirmed in UI | Pinterest → Claim website (tag already present) |
| Boards may be incomplete | Create the 5 SEO boards exactly as named in the 30-day plan |
| Bio/keywords thin | Name: `DigiKitPro \| Procreate Brushes & Tutorials` |
| Masterclass interiors not pinned | New pin set from the 5 real pages (below) |
| Pinterest Tag dormant | Optional: set `PINTEREST_TAG_ID` repo variable |
| Risk of catalog-only pins | Enforce 8 value / 8 technique / 5 shop per 21 pins |

## C3. Board strategy (exact titles)

1. **Procreate Portrait Brushes & Skin Texture Tutorials**  
2. **Procreate Line Art, Inking & Sketch Brushes**  
3. **Procreate Watercolor, Texture & Effects Brushes**  
4. **Procreate Tutorials for iPad Artists** (value)  
5. **Free Procreate Brushes & Free Digital Art Downloads**  
6. **NEW — Procreate Portrait Masterclass** (education board for the 5 interiors + related tutorials)

Board 6 keeps Masterclass searchable without polluting Board 1 with pure ads.

## C4. Keyword strategy (title-first)

Put the search phrase in the **first 5 words** of the pin title:

| Intent | Title stem | Destination |
|---|---|---|
| Skin | Procreate skin texture brushes… | Skin PDP or skin article |
| Portrait workflow | Procreate portrait workflow… | Workflow article / Masterclass |
| Beginner | Free Procreate brushes… | Freebies |
| Masterclass | Inside a Procreate portrait masterclass… | Masterclass PDP |
| Values/light | How light affects form Procreate… | Blog or Masterclass Ch.05 pin |
| Features | How to draw eyes nose lips Procreate… | Masterclass Ch.08 pin |

Description: 150–300 chars, sentence form, 2–3 hashtags max at end. Link the **page**, never the raw image.

## C5. Pin strategy using Masterclass interiors

| Pin | Image | Title | Link |
|---|---|---|---|
| Value | Contents page | 15-chapter Procreate portrait workflow | Masterclass PDP |
| Tutorial | Ch.05 values | Light is design — value structure in Procreate | Skin/workflow article OR Masterclass |
| Preview | Ch.07 skin texture | How to paint realistic skin texture in Procreate | Masterclass PDP |
| Tutorial | Ch.08 features | Eyes nose lips — structure first Procreate | Masterclass PDP |
| Practice | Expression practice sheet | Procreate eye expression practice sheet | Masterclass PDP |
| Shop (1/5) | Cover + price line | Procreate Portrait Masterclass PDF 107 pages | Masterclass PDP |

**Rule:** 4 educational pins : 1 shop pin for Masterclass.

## C6. Traffic strategy

1. Execute existing 30-day calendar (do not invent a second plan).  
2. Week 1–2: freebies + tutorials (saves).  
3. Week 2–4: portrait + Masterclass interiors (clicks).  
4. Every shop pin lands on PDP with upgrade panel + related education.  
5. Monday 5-min review: impressions → saves → outbound → GA4 sessions (`pinterest`).

**Week 4 targets (shape, not promise):** 40k–90k impressions · 600–1,200 saves · meaningful outbound clicks · GA4 Pinterest sessions trending up.

---

# D. MASTERCLASS

## D1. What the 5 real interiors actually contain (no invention)

| # | Page | What it proves | Best use |
|---|---|---|---|
| **1** | **CONTENTS** — 15 chapters, system map, footer: Principles / Exercises / Tools / Troubleshooting / Free resources | Depth, organization, full path | Educational/value · Pinterest pillar · PDP gallery first · IG pin |
| **2** | **Ch.05 Value Structure & Light Design** — “Light is design. Values are your plan.” 6-step value build, 5 value families, squint test, mistakes, practice | Teaching quality, method | Tutorial post · Pinterest tutorial pin · PDP gallery |
| **3** | **Ch.07 Skin Texture & Imperfection** — 6-stage detail process, layer stack, colour harmony, checklist, Portrait Mastery Kit callout | Skin proof + product bridge | Product preview · skin funnel · IG carousel |
| **4** | **Ch.08 Eyes, Nose & Lips** — structure not stickers; 3-pass feature build; mistake fixes | Feature craft | Tutorial · carousel · Masterclass conversion support |
| **5** | **Expression practice — Draw each eye** — reference → sketch → form → detail → practice grid | Practice / workbook feel | Free-value style post · saves · Masterclass conversion |

**Verified product facts (from `products.json` only):** PDF eBook · 107 pages · 15 chapters · $19 · brush-agnostic · free Starter Guide is the on-ramp · includes project walkthrough, checklist, 4-week plan, resource map.

## D2. Rotation system

| Asset | Instagram | Pinterest | Website |
|---|---|---|---|
| **1 Contents** | Pinned value carousel page 1 | Board 6 + Board 4 | PDP gallery #1 · homepage Learn band optional thumb |
| **2 Ch.05 Values** | Education carousel / Reel stills | Tutorial pin → article or PDP | PDP gallery #2 |
| **3 Ch.07 Skin** | Process carousel + Skin Brushes soft CTA | Portrait board + Masterclass board | PDP gallery #3 · Skin PDP “learn the method” |
| **4 Ch.08 Features** | Tutorial carousel | Tutorial pin | PDP gallery #4 |
| **5 Eye practice** | Save-bait carousel · Stories quiz | Practice/workbook pin | PDP gallery #5 · thank-you page “go deeper” |

## D3. Product-page strategy

1. Gallery order: Cover → Contents → Ch.05 → Ch.07 → Ch.08 → Practice.  
2. New section **Inside the Masterclass** with 3 bullets taken only from real pages:  
   - 15-chapter system map  
   - Stage-by-stage method (values → skin → features)  
   - Practice sheets + troubleshooting  
3. Keep format blocks accurate (fixed this session): **How to use it** (PDF), not brush install.  
4. Related: free Starter Guide · Portrait Mastery Kit · Portrait Bundle · skin/hair articles.  
5. No Master Library upgrade panel (fixed).  
6. CTA copy: “Get the Masterclass (PDF)” not “Install brushes.”

## D4. Promotion concepts (ready to produce)

### Instagram

| Concept | Assets | Caption hook | CTA |
|---|---|---|---|
| “What’s inside 107 pages” | 1→3→4 | “I can show you exactly what you get.” | Masterclass link |
| “Light is design” | 2 | Teach squint test in 5 slides | Save + free guide |
| “Details whisper” | 3 | 6-stage detail process | Skin brushes OR Masterclass |
| “Features aren’t stickers” | 4 | 3-pass feature build | Masterclass |
| “Draw the expression” | 5 | Blank practice cells as engagement | Masterclass |

### Pinterest

| Pin type | Title example | Image |
|---|---|---|
| Evergreen tutorial | How to paint better portraits in Procreate | 2 or 3 |
| Workflow | Procreate portrait workflow for beginners | 1 |
| Inside look | Inside a Procreate Portrait Masterclass | 1 |
| Skin | How to paint skin texture in Procreate | 3 |
| Features | Procreate eyes nose lips structure guide | 4 |
| Practice | Procreate eye expression practice sheet | 5 |

### Email (when ESP live)

- Day 4 of sequence already points at portrait workflow → swap hero image to Contents or Ch.05.  
- Post-purchase of Skin Brushes: “Next step — the method behind the texture” + Ch.07 thumb.

## D5. Owner asset drop (required to finish gallery)

Save the 5 supplied PNGs into:

```
assets/products/procreate-portrait-masterclass-ebook/
  interior-01-contents.webp
  interior-02-ch05-values.webp
  interior-03-ch07-skin.webp
  interior-04-ch08-features.webp
  interior-05-eye-practice.webp
```

Then add to `data/products.json` → that product’s `images.gallery` (with widths/heights from the WebP). Rebuild. Until files are on disk in the repo, the strategy above is the rotation map; the PDP still has cover-only gallery.

---

# E. PRIVATE ARTIST RADAR

**Name:** DigiKitPro Artist Radar  
**Hard rule:** separate repo, DB, env, logs, exports. **Never** inside `digikitpro/digikitpro` public site.

## E1. Architecture (MVP)

```
┌─────────────────────────────────────────────────────────────┐
│  digikitpro-artist-radar  (PRIVATE GitHub repo)             │
│                                                             │
│  collectors/     # platform adapters (public data only)     │
│  normalize/      # schema + identity keys                   │
│  score/          # configurable scoring                     │
│  match/          # product recommendation + reason          │
│  suppress/       # DO_NOT_CONTACT permanent                 │
│  export/         # CSV for human review                     │
│  db/             # SQLite first (Postgres later)            │
│  .env            # NEVER committed                          │
│  data/exports/   # gitignored                               │
│  data/raw_cache/ # gitignored, TTL cache                    │
└─────────────────────────────────────────────────────────────┘
         │
         ▼  human only
   CSV → review sheet → manual outreach (Gmail/manual)
```

**Pipeline:** DISCOVER → QUALIFY → SCORE → MATCH → EXPORT → HUMAN REVIEW → MANUAL OUTREACH  

**No automatic email sending. Ever.**

## E2. Recommended tools (researched, with constraints)

| Platform | Tool | GitHub / source | License | Maintenance | Requirements | Limitations | Cost | Radar use? |
|---|---|---|---|---|---|---|---|---|
| **Reddit** | **PRAW** | github.com/praw-dev/praw | BSD-2-Clause | Mature, active | Reddit app credentials, OAuth | API rules + rate limits; no bypass | Free API tier | **YES — Phase 1 primary** |
| **YouTube** | **google-api-python-client** | github.com/googleapis/google-api-python-client | Apache-2.0 | Official | API key, quota | 10k units/day default; search costly | Free quota | **YES — Phase 1** |
| **Web / contact pages** | **requests + BeautifulSoup** / **httpx** | std ecosystem | MIT/BSD | Stable | Respect robots.txt, rate limit | Only public pages | Free | **YES — email discovery** |
| **Email pattern extract** | Custom regex on public contact/about pages only | — | — | — | — | No guessing private inboxes; no SMTP verify harassment | Free | **YES — with source URL** |
| Instagram public | Instaloader | github.com/instaloader/instaloader | MIT | Active but fragile | Often login for scale; ToS risk | Blocks, rate limits; private API risk with alternatives | Free/tooling | **Phase 2 optional, manual-first** |
| Instagram official | Meta Graph API | developers.facebook | — | Official | Business login, app review | Hashtag search capped; not bulk lead gen | Free tier limited | Own-account analytics only |
| X/Twitter | Tweepy | github.com/tweepy/tweepy | MIT | Active | Paid API for useful read volume | Expensive; ToS strict | Paid | **Defer** |
| TikTok | Official Business API / research APIs | — | — | — | Approval | Not a bulk scraper | Varies | **Defer / manual** |
| Pinterest | Official API | developers.pinterest | — | Official | App review | Limited for third-party lead scrape | Free tier | Own pins analytics; not lead scrape |
| Multi-scrape SaaS | Apify actors etc. | apify.com | Proprietary | — | $ | ToS + cost; easy to over-scrape | $$ | **Avoid for MVP** |
| B2B agents (OpenOutreach etc.) | Various | — | GPL/etc | — | Often auto-email | Violates “no auto send” | — | **Do not use send features** |

### Phase 1 platforms (quality > volume)

1. **Reddit** — r/Procreate, r/DigitalPainting, r/learnart, r/ArtistLounge, search “Procreate brushes”, “skin looks flat”, “beginner Procreate”.  
2. **YouTube** — search: Procreate beginner, Procreate portrait, Procreate brushes review (small channels <50k).  
3. **Public websites** — from bios that list a site; crawl `/contact` `/about` only.  
4. **Manual Instagram** — owner saves 20–40 public profiles/week into CSV import template (no bulk scrape until process proven).

## E3. Data model (SQLite `leads`)

Fields exactly as specified in brief §19, plus:

- `evidence_json` — array of `{url, snippet, observed_at}`  
- `category_suggested` — CUSTOMER | CREATOR | EDUCATOR | AFFILIATE_CANDIDATE | POTENTIAL_PARTNER (suggested only)  
- `contact_type` — PUBLIC_BUSINESS_EMAIL | PUBLIC_CONTACT_PAGE | WEBSITE_ONLY | SOCIAL_ONLY  

## E4. Intent detection (weighted keywords)

**Strong (+25–40):** “Procreate beginner”, “learning Procreate”, “what brushes for Procreate”, “paint skin in Procreate”, “Procreate hair”, “Procreate portrait tutorial”, “recommend Procreate brushes”.  
**Medium (+10–20):** “iPad art”, “digital portrait”, “Procreate” + art niche.  
**Weak (+0–5):** generic “digital art” without Procreate.  
**Negative (−20–50):** bot/repost patterns, inactive >180 days, NSFW spam, pure NFT flip spam, already customer (manual tag).

Store `intent_text` + `intent_source_url` always.

## E5. Product matching (transparent)

| Signal | Recommend | Reason template |
|---|---|---|
| Skin / pores / flat face | Portrait Skin Brushes ($5) | “Publicly discussing skin/flatness — specialist texture pack” |
| Hair strands | Hair brushes / stamp kit | “Hair rendering intent” |
| Line art / inking | Essential Line Art Kit | “Line/ink focus” |
| Anime/manga | Anime Soft-Style Kit | “Anime Procreate intent” |
| Watercolor | Watercolor Studio Kit | “Watercolor Procreate intent” |
| Beginner / first portrait | Free Starter Pack + free guide | “Lowest friction entry” |
| Portrait workflow depth | Masterclass ($19) | “Wants method, not only tools” |
| Creator/tutorial | Free pack + affiliate path note | “Creator track — human review” |

Always write `product_match_reason`. Never recommend without why.

## E6. Lead scoring (0–100, configurable)

```
base = 0
+ explicit Procreate        0–25
+ niche match (portrait…)   0–15
+ recent activity (<30d)    0–15
+ learner/problem language  0–20
+ public website            0–10
+ public business email     0–15
+ creator/tutorial signals  0–10
+ product match confidence  0–10
− inactive                  0–20
− unrelated / bot           0–40
− duplicate suppressed      exclude
```

Export default: `lead_score >= 55` AND `suppression_status != DO_NOT_CONTACT` AND `last_verified` within 30 days.

## E7. Deduplication

Conservative keys (merge only if ≥2 agree):

- normalized username + platform  
- website domain  
- identical public business email  
- explicit cross-links in bio (“YT: … IG: …”)

Never merge on display name alone.

## E8. Freshness

- `first_seen`, `last_seen`, `last_verified`, `source`, `source_date`  
- Cache raw responses 7–14 days  
- Re-verify before export if `last_verified` > 30 days  
- Respect rate limits; exponential backoff; stop on 401/403

## E9. Suppression

```
suppression_status: NONE | DO_NOT_CONTACT | ALREADY_CUSTOMER | COMPETITOR | INVALID
suppression_reason: text
suppressed_at: ISO timestamp
```

DO_NOT_CONTACT permanently excluded from all exports. Soft-delete never hard-delete.

## E10. Export CSV columns

`name, platform, profile_url, website_url, public_business_email, contact_type, niche, audience_type, intent_signal, intent_source_url, recommended_product, product_match_reason, lead_score, last_verified, status, category_suggested, notes`

Sorted by score DESC. Cap first export at **100–200** rows for human review.

## E11. Security

- Private repo only  
- `.env` + `data/` + `exports/` gitignored  
- No secrets in Actions logs  
- No lead table on public site, CDN, or Payhip  
- Access: owner machine + private GH  

## E12. MVP build order (Artist Radar only)

| Step | Deliverable | Timebox |
|---|---|---|
| 1 | Private repo + SQLite schema + CLI | 1 day |
| 2 | Reddit collector (PRAW) + intent tagger | 1–2 days |
| 3 | YouTube search collector | 1 day |
| 4 | Website contact extractor (public pages) | 1 day |
| 5 | Score + match + CSV export + suppression | 1 day |
| 6 | Manual Instagram CSV import template | 0.5 day |
| 7 | First 100–200 leads reviewed by human | 1 week ops |

**Do not** build Instagram bulk scraping, auto-DM, or auto-email in MVP.

---

# F. EXPERIMENT PLAN

## F0. Instrumentation baseline (Day 0)

Record one week of:

- GA4: sessions, `product_view`, `outbound_payhip_click`, `email_signup`, `brush_finder_completed`  
- Pinterest Analytics: impressions, saves, outbound  
- IG Insights: reach, saves, link clicks  
- Payhip: orders by product  

Without baseline, nothing is learnable.

## F1. Experiments (run in parallel only if traffic allows; else sequential)

### Experiment A — Small portrait artists (content + site)

| | |
|---|---|
| **Hypothesis** | Portrait-intent traffic converts better on Skin $5 → Mastery $8 → Bundle $15 than generic catalog traffic |
| **Action** | 2 weeks IG+Pinterest only portrait/skin/Masterclass interiors; site: portrait cross-links + Masterclass interiors on PDP |
| **Primary metric** | `outbound_payhip_click` on portrait SKUs / sessions |
| **Secondary** | Masterclass PDP views · free guide downloads |
| **Duration** | 14 days |
| **Stop/go** | If portrait SKU click rate > catalog average → double portrait content share |

### Experiment B — Procreate learners (free funnel)

| | |
|---|---|
| **Hypothesis** | Free Starter Guide + free brushes → email → $5 entry beats cold $19 Masterclass |
| **Action** | Pin/post free guide + free liners daily in value slots; thank-you page starter offer unchanged |
| **Metric** | `email_signup` · free Payhip downloads · assisted $5 purchases (7-day) |
| **Duration** | 14 days |

### Experiment C — Small Procreate creators (Radar + manual)

| | |
|---|---|
| **Hypothesis** | 20 personalized manual outreaches to small tutorial creators yield ≥2 replies |
| **Action** | Radar YouTube+Reddit creators; export 30; manual email/DM with free pack offer + optional review (no auto) |
| **Metric** | Replies · positive replies · tracked sales (UTM `creator`) |
| **Duration** | 21 days |
| **Cap** | 30 contacts max |

### Experiment D — “What brushes do you recommend?” intent

| | |
|---|---|
| **Hypothesis** | Public askers convert when given a workflow answer + one specialist pack |
| **Action** | Reddit monitor via Radar; human replies with genuine tip + free pack link (not spammy); log outcomes |
| **Metric** | Click-through on free link · later purchase |
| **Duration** | 14 days |
| **Ethics** | Helpful first; disclose affiliation if promoting paid |

### Experiment E — Problem niches (skin / hair / line / watercolor / anime)

| | |
|---|---|
| **Hypothesis** | One problem niche will dominate saves+clicks |
| **Action** | Equal content budget 1 week each theme OR A/B pins |
| **Metric** | Saves + outbound by theme |
| **Duration** | 5 weeks or 5 parallel pin sets |
| **Outcome** | Double down winner for 30 days |

## F2. Decision board (after 30 days)

| Signal | Decision |
|---|---|
| Portrait content wins | Make portrait the default hero craft + Masterclass push |
| Free funnel emails grow but no paid | Fix thank-you offer / ESP sequence, not more free |
| Creators reply cold | Pause Radar scale; improve offer |
| Creators reply warm | Build simple affiliate via Payhip native |
| Lifestyle pages high bounce low revenue | Revisit catalog separation |
| Masterclass interiors lift PDP conversion | Roll interior-preview pattern to top kits |

## F3. What we will NOT do in Phase 1

- Raise prices as the main lever  
- Fake reviews / fake student counts  
- Auto-email or auto-DM  
- Giant multi-platform scraper  
- Rebuild the site in a new framework  
- Post only product covers on IG/Pinterest  

---

# Implementation checklist (owner + agent)

### Done this session
- [x] Masterclass install copy fixed (PDF path)  
- [x] Masterclass licence copy fixed  
- [x] Education tier excluded from Master Library upgrade panel  
- [x] Instagram URL wired in site SOCIAL/footer/schema  
- [x] Product pages regenerated  
- [x] This strategy report  

### Owner next (blocking)
- [ ] Drop 5 Masterclass interior images into `assets/products/procreate-portrait-masterclass-ebook/`  
- [ ] Confirm Pinterest website claim + create 5–6 boards  
- [ ] Set IG bio + link-in-bio + highlights  
- [ ] Activate FormSubmit if not already · plan ESP  
- [ ] Create private `digikitpro-artist-radar` repo  
- [ ] Record GA4/Payhip/Pinterest/IG baseline week  

### Agent next (after interiors on disk)
- [ ] WebP optimize + gallery wire + rebuild  
- [ ] Masterclass “Inside” section in generator  
- [ ] Hero CTA → Find My Brushes  
- [ ] Portrait PDP → Masterclass cross-sell band  
- [ ] Optional: scaffold private Radar repo separately  

---

# Success definition (90 days)

DigiKitPro is winning when a stranger can answer in 10 seconds:

1. **What is this?** Procreate tools organized around workflow + portrait education.  
2. **What should I try first?** Free pack or free guide.  
3. **Why trust it?** Real interior proof, real technique content, honest policies.  
4. **What do I buy when ready?** Specialist → kit → bundle/library → Masterclass.

Not when follower count is high. When **discovery → free → email → paid → education** is a measured loop.

---

*Report grounded in live catalog (51 products), existing Phase 1 sales engine, and five real Masterclass interior pages (Contents, Ch.05, Ch.07, Ch.08, Expression practice). No fabricated social proof or interior art.*
