# DigiKitPro SEO Engine — Change Log

**Purpose:** Maintain reversible changes and audit trail per brief non-negotiable safeguard.

**Format:** Date, change, reason, files affected, risk, validation.

---

## 2026-09-19 — Phase 1 Baseline Audit (No production code changes)

- **Date:** 2026-09-19
- **Change:** Created audit deliverables in `docs/seo-audit/` — 01-platform-and-safeguards, 02-url-inventory, 03-issue-register, 04-metadata-schema-linking-gaps, 05-assumptions-and-manual-review, 06-proposed-architecture, 00-executive-summary, 07-monitoring-report, CHANGELOG.
- **Reason:** Phase 1 audit per brief section 3 — crawl and code/configuration review, no implementation.
- **Files affected:** `docs/seo-audit/*` only (documentation, no HTML/CSS/JS/data changes).
- **Risk:** Low — documentation only, no impact on production URLs, metadata, analytics, Pinterest catalog.
- **Validation:** Build still passes (99 sitemap URLs, 51 products, 18 blog md), verify.py 87/88 (2 broken links in orphaned drafts — pre-existing).
- **Safeguards:** Preserved all existing product/article/category URLs, redirects, canonicals, analytics, structured data, Pinterest feeds. No invented content.

---

## 2026-09-20 — Retire the public /seo-audit/ HTML (docs stay internal)

- **Date:** 2026-09-20
- **Change:** Removed the 11 published audit pages (`/seo-audit/` index + 10 sub-pages: 00-executive-summary … 08-approval-gate + changelog). `tools/build.py` no longer imports `pages_audit` or calls `build_audit()`; `tools/pages_misc.py` no longer injects audit URLs into `sitemap.xml` / `sitemap.txt`. `tools/verify.py` went 90 → 88 checks: the two sitemap-presence checks retired with the pages, and the `seo-audit` carve-outs in the github.io and honesty scans were dropped. `tools/pages_audit.py` is kept on disk but is no longer invoked.
- **Reason:** The audit deliverable is an internal working document, not storefront content — it should not be crawlable, indexed, or competing with commercial pages.
- **Files affected:** `seo-audit/**` (11 HTML files deleted), `tools/build.py`, `tools/pages_misc.py`, `tools/verify.py`, `sitemap.xml`, `sitemap.txt`. `docs/seo-audit/*.md` (10 documents + this changelog) are unchanged and remain the internal source of truth.
- **Risk:** Low — reversible via git. The retired URLs were never in the main navigation; nothing else linked to them.
- **Validation:** `python3 tools/build.py` → `sitemap.xml` and `sitemap.txt` at 101 URLs each, 0 `/seo-audit/` entries (was 112 with 11 audit URLs); `python3 tools/verify.py` → ALL 88 CHECKS PASSED.
- **Safeguards:** 18 blog articles, 51 product pages, 10 categories, 2 season hubs, 6 buyer guides, the partner portal and both SEO tools (`/tools/` + `/tools/canvas-calculator/`) are untouched. No existing URL, canonical, redirect, analytics tag, structured-data block or Pinterest feed changed.

---

## Future Changes (Template)

### Example entry for safe fix

- **Date:** YYYY-MM-DD
- **Change:** Fixed broken internal links in procreate-mistakes-beginners — pointed to existing articles procreate-canvas-size-dpi-guide and best-procreate-brushes-for-beginners.
- **Reason:** Issue C-01 — broken links fail verify and cause crawl waste.
- **Files affected:** `content/blog/procreate-mistakes-beginners.md` (if converted to md) or removal of orphaned HTML dirs, `tools/build.py` rebuild.
- **Risk:** Low — reversible via git, no URL change for existing 18 articles.
- **Validation:** `python3 tools/build.py && python3 tools/verify.py` — expected 88/88, sitemap still 99 or 103 if new articles added, no new broken links, canonicals correct, OG dimensions correct.

---

**End of change log.**
