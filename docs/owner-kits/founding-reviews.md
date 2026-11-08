# Owner kit — Founding Reviews (collect 3 quotes, fill the launches)

**Why this exists:** the site currently has **zero buyer social proof**. Every competitor in [`../growth-strategy-2026-11/02-competitor-intelligence.md`](../growth-strategy-2026-11/02-competitor-intelligence.md) exposes counts — RetroSupply 4.9★/395, Kimmyw 1,106 sales, Gabrielle 8.8k sales/1.1k reviews. DigiKitPro ships better craft and better proof-of-work, and shows nothing. This kit is the fastest honest fix.

**What is now live in the code (this branch's PR):**

- Product pages render a **Reviews** section automatically **only if** `data/products.json` carries real quotes for that product (`reviews` array). No quotes → nothing renders. No placeholders, no invented content on live pages.
- Product JSON-LD embeds those quotes as schema.org `Review` nodes with `author` and `reviewBody`, and `reviewRating` **only when you enter an integer 1–5**. An `AggregateRating` is deliberately never synthesised from a handful of quotes (that would be misleading and is testing risk you do not want).
- CSS in `css/style.css` (`.review-grid`, `.review-card`, `.review-rating`) is ready.

## What you (the owner) do — ~30 minutes

1. **Source real quotes.** Your only legitimate sources: organic emails/Payhip messages, replies via contact form, DMs you already have, reviews left on Payhip (if Payhip shows them), or post-purchase emails you send now. Do not use friends-and-family pretend purchases or compose quotes yourself — that is fabrication and it is against Payhip terms, FTC guidance and plain honesty.
2. **Pick up to 5 recent buyers** on the flagship SKUs first: `portrait-skin-brushes-procreate`, `portrait-mastery-kit-46-brushes`, `ultimate-portrait-mastery-bundle`, `essential-line-art-sketch-kit`. A short ask beats a perfect survey.
3. **Copy quotes verbatim** — typos, grammar, enthusiasm, whatever. Ask permission (email first) to publish name + quote. Use first name + last initial + a role line if they give one.
4. **Paste into `data/products.json`.** Shape (per product):
   ```json
   "reviews": [
     {
       "quote": "<verbatim customer words>",
       "name": "First L.",
       "role": "Procreate user since 2024 · optional",
       "rating": 5
     }
   ]
   ```
   `rating` optional — omit it if the customer did not give a star number. Never estimate it.
5. **Rebuild and check:** `python3 tools/build.py` then `python3 verify.py && python3 tools/qa_seo.py && python3 tools/qa_product_editorial.py`.
6. Open a PR (or extend this one) and paste the sent consent + sources in the description. **Never commit private info beyond first-name/last-initial + role.**

## Outreach email (adapt freely)

> Subject: 30 seconds — what did you think of your brush kit?
>
> Hi {first name},
>
> I'm the maker behind DigiKitPro ({product name}). I'm not asking for anything positive — I'm collecting honest words from the first buyers so new artists can decide fairly. If you loved it, say so. If something was confusing, say that too — I fix what I can.
>
> Would you mind a sentence or two about what you used it for? And one to five stars if you give ratings — or no rating at all, just words.
>
> Reply or reach me here. Either way, thank you for the purchase.

## Honesty rules (hard)

- Never write/pay/reward for positive reviews. If you offer any incentive, it must not depend on the review's sentiment, and it must say so.
- Never aggregate or average small samples into a store-wide rating.
- Never copy quotes from marketplace listings without permission.
- Keep replies in your inbox — the repo carries only consenting, anonymised-as-agreed material.

## Success measure

≥3 quotes on ≥2 of the flagship PDPs · zero fabricated entries · optional `reviewRating` only where stars were given verbally/in writing by the customer.
