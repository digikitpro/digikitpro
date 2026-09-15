# DigiKitPro — Pinterest 30-Day Plan (3 pins/day, 5 SEO boards, Idea Pins)

Account: **https://www.pinterest.com/DigiKitProStudio/**
Goal for the 30 days: turn the account into the #1 cold-traffic source for the site — 90 fresh
pins, 5 keyword-loaded boards, 12 Idea Pins, and clicks that land on real product pages and
blog guides (not on image files).

Two honesty rules this plan never breaks, because they are also site policy:

1. **No bought numbers.** No follower purchases, no engagement pods, no "pin exchange" groups,
   no mass follow/unfollow. Apart from being against Pinterest's terms (which can suppress or
   ban the account), it buys nothing this store needs — Pinterest distributes *fresh, keyworded
   pins*, not follower counts.
2. **No invented claims** in pin text. No "10,000 artists use this", no fake before/after, no
   "only 3 left". Every number on a pin (1,200 swatches, 2,000+ brushes, 107 pages, 15 chapters)
   comes from `data/products.json` — the same numbers the product page prints.

What "fast" realistically means here: Pinterest starts showing fresh pins within hours and
keeps ramping them for weeks (unlike Google, there is no sandbox). Expect impressions in the
first 48 hours, meaningful outbound clicks in weeks 2–4, and the tail continuing to compound
after day 30. Nothing legitimate produces a traffic spike on day one — but nothing here waits
on domain authority either.

---

## 1. What is already wired on the site (nothing to build)

| Piece | Status | Where |
|---|---|---|
| Domain claim tag | **Live on all 95 pages** — `<meta name="p:domain_verify" content="990d08b5349bfcbb0171eab3d6f8f2d2"/>` | `PINTEREST_VERIFY` in `tools/core.py` |
| Profile link (footer band + follow CTA) | Live | `PINTEREST_PROFILE` in `tools/core.py` |
| Save button on every product image | Live — cards, homepage ladder, best-seller band, bundle panels, eBook covers, freebie cards, product gallery, upgrade panel | `pin_button()` |
| Pin data (page + artwork + description) | Live — `data-pin-*` on every product image | `pin_attrs()` |
| Product Rich Pins | Live on paid product pages (`og:type=product` + real price/currency/availability/brand) | `head()` |
| Share rows (Pin / Facebook / X / WhatsApp) | Live on all 51 product pages + 18 articles | `share_buttons()` |
| Pinterest Tag | **Dormant until you set it** — repo variable `PINTEREST_TAG_ID` | `.github/workflows/deploy.yml` |

**Owner: 30-minute setup (do this before pin #1)**

1. Pinterest → Settings → **Claim** → *Claim your website* → enter `https://digikitpro.shop`.
   The tag is already on every page, so the claim verifies instantly (HTML-tag method).
2. Pinterest → Settings → **Bulk create** / *Rich Pins* → validate one product URL, e.g.
   `https://digikitpro.shop/products/portrait-skin-brushes-procreate/` → **Apply now**.
   Rich Pins show the live price and "In stock" on every pin of that page.
3. Account → **Business account** (free): unlocks analytics, the free native scheduler
   (schedule up to 2 weeks ahead) and ads later if you ever want them.
4. Profile: name `DigiKitPro | Procreate Brushes & Tutorials`, bio with the keywords people
   actually search (`Procreate brushes, iPad art tutorials, free brush packs — instant download`).
5. Create the **5 boards** below with the exact titles/descriptions (keywords live in the board
   title, not just the pin).
6. *(Optional, 2 minutes)* add the repo variable `PINTEREST_TAG_ID` if you want Pinterest-side
   conversion tracking; leave it unset and no Pinterest script beyond the save button loads.

---

## 2. The 5 SEO boards (create once, pin into forever)

Pinterest is a search engine: board titles and descriptions are indexed, and a board that mixes
topics ranks for nothing. These five split the real catalogue along **search intent**, not along
`data/products.json` categories.

| # | Board title (exact) | Board description (paste as-is) | Primary pins | Target pages |
|---|---|---|---|---|
| 1 | **Procreate Portrait Brushes & Skin Texture Tutorials** | Procreate portrait brushes, skin texture brushes and step-by-step portrait tutorials for iPad artists. Realistic skin, blending, hair and finishing — plus free brush packs to start with. | Skin texture, portrait kits, portrait workflow guides, blending | `/category/portrait/`, `/category/skin-texture/`, `portrait-skin-brushes-procreate`, `portrait-mastery-kit-46-brushes`, blog: realistic skin, skin texture, blending, portrait workflow |
| 2 | **Procreate Line Art, Inking & Sketch Brushes** | Fine liner, micron, marker and sketching brushes for Procreate — plus how to get clean line art on iPad. Free liner pack included. | Line art kits, liner/marker studio, sketchbook sets, figure-drawing stamps, tattoo line work | `/category/line-art/`, `/category/sketching/`, `/category/figure-drawing/`, `master-line-art-vault-300-brushes`, free liner set, blog: line art, tattoo design, stamp vs painting brushes |
| 3 | **Procreate Watercolor, Texture & Effects Brushes** | Watercolor, glitter, smoke, charcoal and pastel brushes for Procreate. Organic texture, paper grain and light effects — with tutorials for each medium. | Watercolor kits, glitter/smoke/effects, charcoal, pastel, chalk, paper textures, animal fur | `/category/watercolor/`, `/category/glitter-effects/`, `/category/traditional/`, blog: watercolor, traditional look |
| 4 | **Procreate Tutorials for iPad Artists** (value board) | Technique-first Procreate tutorials: brushes, blending, canvas size, DPI, installation, workflows. Everything we learn while painting goes here first. | The 18 long-form guides as Idea Pins and 2:3 graphics | `/blog.html` + each `/blog/<slug>/` |
| 5 | **Free Procreate Brushes & Free Digital Art Downloads** | Free Procreate brush packs, free palettes and a free portrait starter eBook — instant download, no email required. New freebies land here first. | The 4 free products + free-guide pages | `/freebies.html`, free product pages, `procreate-starter-guide-free-ebook` |

**Sections (board sub-groups) worth adding:** Board 1 → `Skin texture` / `Hair` / `Blending`;
Board 2 → `Fine liners` / `Sketching` / `Figure drawing`; Board 3 → `Watercolor` / `Glitter & smoke` /
`Charcoal & pastel`. Sections are extra keyword surface for free.

**What NOT to create:** a "Procreate Brushes" everything-board. It would slice the same catalogue
in half and rank for nothing against the boards above.

---

## 3. Formats, sizes and text rules

| Format | Size | Use | Notes |
|---|---|---|---|
| Static pin (2:3) | **1000 × 1500 px** | 2 of the 3 daily pins | Pull artwork from `assets/products/<slug>/…-card.webp` and upscale/crop to 2:3, or use the product's `full` art |
| Idea Pin (multi-page) | **1080 × 1920 px** | 3 per week, one per board | 3–7 pages: hook → 3 steps → result → CTA. Native to the feed, highest reach per pin today |
| Video pin / Idea Pin video | 1080 × 1920, **15–30 s** | 1–2 per week | Screen-record the brush strokes in Procreate; no talking needed |
| Carousel-ish "before/after" | 1000 × 1500 | Board 1 & 3 | Brush off vs brush on — the highest-saving format for this niche |

Text rules that decide whether a pin travels:

- **First 5 words of the title** carry the keyword: `Procreate skin texture brushes — realistic pores in 3 steps`.
- Title ≤ 40 characters where possible, description 150–300 characters, written as a sentence
  (Pinterest reads it as text, not tags).
- **2–3 hashtags maximum**, always at the end: `#procreatebrushes #procreatetutorial #digitalart`.
  Keyworded sentences beat hashtag stuffing on Pinterest every time.
- Text overlay in the image: ≤ 6 words, big, top third. Never repeat the whole description.
- **Alt text** on every pin (Pinterest → pin edit): describe artwork + keyword once.
- Link the **page**, never the image: product page for shop pins, guide for tutorial pins.
  With Rich Pins live, the price appears under the pin automatically.
- Fresh pin every time: re-uploading the same file again is treated as a duplicate. Change the
  crop, the overlay text or use another gallery image from the product (`images.gallery[]` gives
  you 3–4 alternate artworks per product).

---

## 4. The daily rhythm (3 pins/day = 90 pins in 30 days)

Publish in three fixed slots so the account always looks alive in three different day-parts.
**09:00 / 13:00 / 19:00 US Eastern** is the standard craft-and-DIY window; verify against your
own analytics in week 3 and shift if your audience reads differently.

| Slot | Board rotation | Content | Why |
|---|---|---|---|
| **09:00 — Value pin** | Boards 4 + 5 | Tutorial graphic or freebie | Builds saves and follows (saves are the strongest ranking signal) |
| **13:00 — Idea Pin** (Mon/Wed/Fri) or fresh static | Boards 1–3 | Artwork, technique, process | Idea Pins reach non-followers, which is how a new account grows |
| **19:00 — Shop pin** | Boards 1–3 (rotating) | Product artwork with price/asset line | Captures the saved-for-later buyer; only ~1 in 3 pins is a shop pin |

Weekly mix over 21 pins: **8 value/free pins, 8 Idea Pins or artwork/technique pins, 5 shop pins.**
Never post three shop pins in a row — the feed punishes pure catalog accounts.

**Batch production (3 hours, covers 2 weeks):**
1. Export 24 pin images from product art + blog heroes (`assets/products/…`, `assets/img/…`).
2. Write 24 titles/descriptions from the templates in §6 (one Google Doc, paste into Pinterest).
3. Schedule them 2 weeks ahead with Pinterest's native scheduler (free) — or publish manually
   in the three slots if you prefer the app's "fresh pin" timing.

---

## 5. 30-day calendar

Week themes follow seasonal search demand: portraits and watercolor carry the broad
`procreate brushes` demand; the Christmas set starts early because Pinterest shoppers plan
6–8 weeks out (that board is indexed before the seasonal rush, not during it).

### Week 1 — Foundations + product coverage (boards warm up)
| Day | 09:00 value pin | 13:00 | 19:00 shop pin |
|---|---|---|---|
| 1 | Board 5: free liner set — "100 free Procreate liner brushes" | **Idea Pin**: install a .brushset in 4 taps | Board 1: `portrait-skin-brushes-procreate` artwork |
| 2 | Board 4: canvas size & DPI guide | Static: portrait workflow step 1 (sketch) | Board 2: `master-line-art-vault-300-brushes` |
| 3 | Board 5: free colour vault (1,200+ swatches) | Static: watercolor bloom close-up | Board 3: `50+ realistic watercolor studio kit` |
| 4 | Board 4: blending without plastic skin | **Idea Pin**: 3 brushes, 3 textures | Board 1: `portrait-mastery-kit-46-brushes` |
| 5 | Board 5: free portrait starter eBook | Static: charcoal on texture paper | Board 3: `smoke procreate brushes` |
| 6 | Board 4: stamp brushes vs painting brushes | **Idea Pin**: hair in 5 strokes | Board 2: `essential-line-art-sketch-kit` |
| 7 | Board 5: chalkboard toolkit (free) | Static: anime soft-style face | Board 1: `artista-studio-kit-76-brushes` |

### Week 2 — Technique depth + freebie push
| Day | 09:00 value pin | 13:00 | 19:00 shop pin |
|---|---|---|---|
| 8 | Board 4: realistic skin, layered workflow | **Idea Pin**: skin texture in 3 layers | Board 1: ultimate portrait bundle |
| 9 | Board 5: free liner set (new crop) | Static: glitter close-up | Board 3: `30 glitter brushes` |
| 10 | Board 4: make digital art look traditional | Static: pastel blend | Board 3: `dreamy pastel art kit` |
| 11 | Board 5: free colour vault (palette grid) | **Idea Pin**: 4 paper textures, 4 looks | Board 2: `professional liner & marker studio` |
| 12 | Board 4: how to choose Procreate brushes | Static: figure drawing stamp | Board 2: female pose stamps |
| 13 | Board 5: starter eBook (page preview) | **Idea Pin**: anime shading pass | Board 1: anime soft-style kit |
| 14 | Board 4: hair without drawing every strand | Static: 650-brush bundle cover | Board 3: master vault mega bundle |

### Week 3 — Idea Pin sprint + seasonal runway
| Day | 09:00 value pin | 13:00 | 19:00 shop pin |
|---|---|---|---|
| 15 | Board 4: tattoo design sketch → stencil | **Idea Pin**: koi tattoo line work | Board 2: tattoo studio kit |
| 16 | Board 5: free liner set (video crop) | Static: animal fur detail | Board 3: `animal fur 2` |
| 17 | Board 4: watercolor realism tutorial | **Idea Pin**: wet-on-wet in 20 s | Board 3: `80 organic watercolor brushes` |
| 18 | Board 5: free eBook (chapter list) | Static: Christmas card artwork | Board 3/seasonal: Christmas bundle |
| 19 | Board 4: portrait workflow, final polish | **Idea Pin**: before/after polish | Board 1: `portrait skin brushes` (new crop) |
| 20 | Board 5: free chalkboard toolkit | Static: smoke + light | Board 3: `10 premium texture & effects` |
| 21 | Board 4: GoodNotes planner pages (lifestyle wedge) | Static: 2026 wellness journal spread | Board 5: planner/journal bundle |

### Week 4 — Compound what worked + plan next month
| Day | 09:00 value pin | 13:00 | 19:00 shop pin |
|---|---|---|---|
| 22 | Board 4: best brushes for beginners | **Idea Pin**: start-here kit | Board 1: beginner starter picks |
| 23 | Board 5: free palettes | Static: master library cover | Board 1/2/3: `master library 2,000+` |
| 24 | Board 4: blending brushes deep dive | **Idea Pin**: blend a cheek in 15 s | Board 1: skin brushes |
| 25 | Board 4: canvas size for prints | Static: line art detail | Board 2: sketchbook brushes |
| 26 | Board 5: free liner set (seasonal crop) | **Idea Pin**: Christmas bauble | Board seasonal: Christmas bundle |
| 27 | Board 4: iPad brush installation FAQ | Static: Halloween pumpkin | Board seasonal: Halloween PNGs |
| 28 | Board 5: free starter eBook | **Idea Pin**: what's inside the masterclass | Board 4: masterclass eBook ($19) |
| 29 | **Best performer of weeks 1–3, re-shot as a new pin** | Static: best seller artwork | Board 1: best seller |
| 30 | **Round-up pin: "12 Procreate brushes we actually use"** | **Idea Pin**: month recap | Board 1: the bundle ladder top rung |

Day 29–30 are deliberate: Pinterest rewards the format that already earned saves on *this*
account, and a round-up pin is the cheapest way to convert a month of traffic into bundle sales.

---

## 6. Copy templates (fill in, keep the keyword first)

**Shop pin (Board 1 example)**
> Title: `Procreate skin texture brushes — pores, freckles, wrinkles`
> Description: `19 skin-texture brushes for Procreate: pores, freckles, wrinkles and textured blenders that turn flat paintings into believable portraits. Instant download, $5. #procreatebrushes #procreatetutorial`
> Link: `https://digikitpro.shop/products/portrait-skin-brushes-procreate/`

**Tutorial pin (Board 4)**
> Title: `How to paint realistic skin in Procreate`
> Description: `Layer-by-layer workflow for realistic skin in Procreate: base, texture, blend, finish. Free starter guide included. #procreatetutorial #digitalpainting`
> Link: `https://digikitpro.shop/blog/how-to-create-realistic-skin-in-procreate/`

**Freebie pin (Board 5)**
> Title: `Free Procreate liner brushes — 100 brushes, no email`
> Description: `Download 100 fine liner and micron brushes plus 13 paper textures for Procreate. Free, instant, no email required. #freeprocreatebrushes #procreate`
> Link: `https://digikitpro.shop/products/free-fine-liner-brushes-100/`

**Idea Pin hook (page 1 text)**
> `3 brushes. 1 believable face.` → pages: brush → pass → blend → result → `Full kit: 46 brushes, $8` (last page links the product page).

Keyword bank to rotate inside the copy (use 2–4 per pin, never all):
`procreate brushes`, `procreate portrait brushes`, `skin texture brushes`, `procreate line art brushes`,
`free procreate brushes`, `procreate watercolor brushes`, `procreate tutorial`, `how to paint in procreate`,
`ipad art tutorial`, `digital art brushes`, `procreate brush pack`, `procreate glitter brushes`.

---

## 7. Measurement — 5 minutes every Monday

Log these from Pinterest Analytics (Business account) and GA4 (`dkp.track` events already fire
on buy clicks and free downloads):

| Metric | Where | Week 2 target | Week 4 target |
|---|---|---|---|
| Impressions | Pinterest → Analytics | 10k–25k | 40k–90k |
| Saves | same | 150–300 | 600–1,200 |
| Outbound clicks | same | 300–600 | 1,200–2,500 |
| Sessions from Pinterest | GA4 → Traffic acquisition (`pinterest`) | 150–400 | 700–2,000 |
| Buy clicks (`product_buy_click`) | GA4 / `dkp.report()` | first sales | steady |

Those ranges are realistic for a fresh account posting 3 consistent, keyworded pins a day with
5 focused boards — not a promise, and the honest floor is lower if only one format gets posted.
Read them as the shape of a normal ramp: saves lead clicks by about a week, clicks lead sales by
another.

**If it is flat after 14 days:** the cause is almost always one of these three, in this order —
(1) titles that do not contain a searched phrase, (2) boards that mix unrelated topics,
(3) the same image re-uploaded. Fix in that order before touching posting volume.

**What to do with a winning pin:** re-shoot it (new crop/overlay) weekly, add it to two more
boards, and point it at the *bundle ladder* — the pin that sells a $5 kit should be the same pin
that upsells the $15 bundle on the product page (the upgrade panel is already there).

---

## 8. Rules that keep the account safe

- No bought followers, no pods, no mass follow/unfollow, no comment spam on competitor pins.
- No claims of popularity, ratings or scarcity in pin copy — the site's honesty guard exists for
  the same reason, and the same standard applies to pins.
- Only post artwork from the products in `data/products.json` (real, licensed, owned) — never a
  Pinterest-find re-uploaded as your own.
- One link per pin, going to a page that exists (every pin link above is a live page today).
- If a product is removed from the store, archive its pins rather than leaving dead links —
  `python3 tools/payhip_sync.py` keeps `data/products.json` in sync, so the site side is handled.
