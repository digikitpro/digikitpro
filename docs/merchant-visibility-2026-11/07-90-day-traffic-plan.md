# Phase 7 — 90-Day Traffic Growth Plan (2026-11-08 → 2027-02-06)

Format per brief: **Days 1–15 Foundations · 16–30 SEO · 31–60 Traffic · 61–90 Conversion & Expansion**. Each row: Priority (P0/P1/P2), Impact (High/Med/Low), Difficulty (Easy/Med/Hard), KPI. Execution rules hold: nothing live without your approval; docs are ready to hand to whoever executes. Owner = what we can prep vs what only you can do.

## Measurement note first

Baseline must precede change, or this plan is faith, not measurement. **First milestone (Day 3):** GSC + MC exports filed to `baseline-data/` and `08-measurement-dashboard.md` §1 filled. Every "week N" target below assumes that baseline exists; targets are written as deltas-to-baseline, not absolutes, precisely because baseline is unknown.

---

## Days 1–15 — Merchant Center & visibility foundations

Goal: make the 44 listings legally eligible and technically fetchable. Nothing here is SEO; it is the price of admission.

| # | Action | Prio | Impact | Diff. | KPI / exit criterion |
|---|---|---|---|---|---|
| 1 | OWNER: **MC → Shipping & returns**: configure US shipping service for digital goods (0 USD) — mandatory; then confirm other listed countries if you want them | P0 | High | Easy | MC shows shipping active; fetch picks up change |
| 2 | OWNER: **MC → Marketing → Marketing methods**: confirm Free listings card = ON (Admin access) | P0 | High | Easy | Screenshot in baseline-data/ |
| 3 | OWNER: **MC → Settings → Business information**: return-policy URL (`refunds.html`) added in MC | P0 | Med | Easy | Refunds URL shown in MC |
| 4 | OWNER: **MC → Products → Needs attention**: screenshot every warning/disapproval with item IDs; file to baseline-data/; Triage script: category override flag F decision (keep 500046/8022 vs revert) | P0 | High | Easy-Med | Zero unexplained flags; F decision recorded |
| 5 | Trigger feed re-fetch; verify 44 items show approved; spot-check `identifier_exists=no` accepted, highlights picked up | P0 | High | Easy | 44/44 "approved" (or explicit disapprovals documented) |
| 6 | Publish baseline dashboard (`08-measurement-dashboard.md`); un-pause if owner delivered exports Day 3 | P1 | Med | Easy | Dashboard §1 complete |
| 7 | pinterest: audit pin templates, 2 flagship pins for portrait-skin + mastery-kit (Pinterest = our gap closure) | P1 | Med | Med | Pins live; outbound links verified |
| 8 | P2 feed polish from `03-optimization-44-products.csv`: owner decides the 8 under-bar highlight items — add genuine facts or accept status quo (no padding) | P1 | Med | Med | Each item either enriched (real facts) or explicitly accepted |
| 9 | 21→ solder 5 zero/hero gap items if approved (skip; proposal-only): email outreach to recent buyers for founding reviews | P2 | Med | Med-Hard | ≥5 review asks sent |
| 10 | PR #82 decision point: merge/enable System bundle go-live path (Payhip listing → wiring PR) | P2 | Med | Med | Owner decision recorded |

Exit criteria (Day 15): Free listings ON + US shipping live + zero unexplained MC flags + baseline filed. **Any of these failing = stop and fix; do not proceed to Days 16–30 expecting impressions.**

---

## Days 16–30 — SEO & landing-page foundations

Goal: every feed destination and every article is a high-CTR, conversion-ready surface with honest internal linking.

| # | Action | Prio | Impact | Diff. | KPI |
|---|---|---|---|---|---|
| 11 | Ship **PDP improvements** Phase 4 P1: compatibility+licence box near CTA, install-help strip (2 lines + link), reviews block on top-4 PDPs (Skin / Mastery / Essential Line Art / Bundle) | P1 | High | Med | New PDP template live; passed QA (all suites green) |
| 12 | Internal-link pass: PDP→guide, guide→PDP, freebie→paid rung anchors — programmatic where possible (`tools/` or editorial check), spot-check 100% | P1 | High | Med | 104/104 pages; zero orphan PDPs |
| 13 | Category hub intros rewritten as evergreen entry points (portrait, line-art, watercolor, anime) with CollectionPage schema; noindex removed if policy permits | P1 | Med-High | Med | 4 hubs refreshed; qa_seo green |
| 14 | Alt-text + gallery crop audit on the 8 P2 highlight/single-image items; request owner assets for 6 single-image listings | P1 | Med | Med | 100% images alt-checked; hero crops ≥1200px |
| 15 | GSC striking-distance review: export → filter pos 5–20, impressions>50 → refresh those pages (title/date/FAQ); resubmit | P1 | High | Med | ≥5 pages refreshed; GSC re-index requested |
| 16 | Structured-data spot-check in Rich Results Test: 5 PDPs + 2 guides | P2 | Med | Easy | No fatal errors |
| 17 | Licence specificity: state commercial/personal tier per flagship kit (owner confirms licence lines) | P2 | Med | Easy-Med | Licence lines visible on top-4 PDPs |

Exit criteria (Day 30): top-4 PDPs rebuilt, internal-link map applied site-wide, striking-distance pages refreshed, GSC export baseline in place.

---

## Days 31–60 — Traffic acquisition (organic channels)

Goal: ship the demand engine: targeted content + Pinterest cadence + outreach — all aimed at existing PDPs (no new content for content's sake).

| # | Action | Prio | Impact | Diff. | KPI |
|---|---|---|---|---|---|
| 18 | Publish **Skin Clenie cluster completion**: "freckles & pores in Procreate" tutorial (search gap confirmed 2026-11-08; map to Skin Kit) | P1 | High | Med | Article live; structured data; pins added |
| 19 | Publish **"procreate brush bundle portrait" buyer's guide** bridging to Ultimate Bundle / System Bundle (honest: when to buy vs build) | P1 | High | Med | Live + internal links to both bundles |
| 20 | Refresh **how-to-install-procreate-brushes** into the PDP install strip's target (dedup, FAQPage alignment with PDPs) | P1 | Med | Med | Install CTR monitored |
| 21 | **Pinterest cadence**: 2 pins per new/refreshed article + 1 before/after pin per flagship PDP weekly; link to PDP UTM source `pinterest` | P1 | High | Easy-Med | 20+ pins/mo; outbound clicks tracked |
| 22 | **Listicle outreach**: personalised pitch to 10 brush-roundup/blog editors (bebrushes.com, brusher.art, maker/illustration lists) with demo GIF + honest paragraph | P1 | Med-High | Hard | ≥3 replies; ≥1 placement target |
| 23 | Reddit value-first participation: r/ProCreate, r/ProCreateBrushes, r/DigitalPainting — answer with guides, not product links | P2 | Med | Med | 10 substantive comments; ref traffic to freebie pages |
| 24 | Email mini-sequence for new freebie signups (3 emails: install help → technique tip → honest paid offer) | P2 | Med-High | Med | ESP sequence live; open/click tracked |
| 25 | Repurpose install + skin guides into 2 Instagram/Pinterest carousels (if socials are in scope for you) | P3 | Low-Med | Med | Posted; UTM tracked |

Exit criteria (Day 60): 2–3 new/refreshed articles, Pinterest engine live, outreach sent, ESP sequence active. **Monitor**: organic sessions +20–30% vs baseline (adjust in Day-60 review) — not a guarantee; direction only.

---

## Days 61–90 — Conversion & expansion

Goal: turn visibility into orders; expand what's proven; stop what isn't.

| # | Action | Prio | Impact | Diff. | KPI |
|---|---|---|---|---|---|
| 26 | **Conversion review of top-4 PDPs** with real data: add to cart/order rate via Payhip; if CVR < baseline by 30%+, iterate copy/urgency/cta once — measure 14 days | P1 | High | Med | Payhip CVR for 4 PDPs; iteration shipped if triggered |
| 27 | Launch **Bundle A2 → "The Complete Portrait System" ($25)** after PR #82 merge: Payhip listing, cover art (owner), wiring PR, feed re-fetch | P1 | High | Med | Bundle live; first orders; feed shows 45 items |
| 28 | **Bundle attach funnel**: post-purchase "complete your kit" smart link on PDPs of component kits | P2 | Med | Med | Bundle attach ≥15% of component sales |
| 29 | **Hero-gap product decision**: zero-impression SKUs test — 2 weeks after eligibility fix, if <10 impressions & no flag → propose feed exclusion to cut noise | P2 | Low-Med | Easy | Decision memo per item |
| 30 | **Second content wave** (only if Days 31–60 metrics justify): anime-cluster article refresh + Christmas/Halloween seasonal rotation plan (peak windows) | P2 | Med | Med | Article live before peak |
| 31 | **Case studies/results one-sheet** from founding reviewers → PDP proof blocks | P2 | Med | Hard | 2 quotes integrated |

Exit criteria (Day 90): measured delta vs baseline on: MC impressions+clicks, organic sessions to PDPs, freebie→email rate, paid order count & bundle attach — presented in the Month-3 dashboard review with go/no-go for wave 2.

---

## Weekly cadence (owner + whoever executes)

- **Mon:** check MC Diagnostics (anything new?) — 2 min
- **Tue/Thu:** Pinterest pins; comment moderation
- **Fri:** 30-min metrics glance (impressions, clicks, CTR, orders) vs dashboard alerts
- **Every 2 weeks:** one small experiment shipped (per week ladder above)

## What will NOT move the needle (don't do them)

- Keyword-stuffed rewrites, duplicate thin articles, bought backlinks, engagement pods, 45-SKU marketplace duplication — all burn trust with both Google and buyers.
- "Set and forget" — GSC/MC decay without quarterly refresh; calendar it.
- Reacting to single-day swings — 28-day windows or it isn't a trend.

## Dependencies & risks

- **US shipping step (Day 1–15 #1) is the gate** — everything downstream assumes it.
- Pro-sketch (#H) may re-enter feed any time — review before every fetch.
- Bundle A2 launch depends on PR #82 owner merge + Payhip listing creation — if deferred, Day 61–90 #27 slides; keep plan intact otherwise.
- If GSC reveals no striking-distance pages, swap Days 16–30 #15's effort into #12 (internal links) and note it.
