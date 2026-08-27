#!/usr/bin/env python3
"""Visual QA for this round: marquee band, article thumbnails, newsletter form."""
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000"

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_context(viewport={"width": 1440, "height": 900}).new_page()

    # ── homepage: marquee band ──
    pg.goto(BASE + "/", wait_until="networkidle")
    pg.wait_for_timeout(1200)
    pg.locator(".cat-marquee").scroll_into_view_if_needed()
    pg.wait_for_timeout(400)
    t0 = pg.evaluate("getComputedStyle(document.querySelector('.cat-track')).transform")
    pg.wait_for_timeout(800)
    t1 = pg.evaluate("getComputedStyle(document.querySelector('.cat-track')).transform")
    print("marquee animating:", t0 != t1, "|", t0, "->", t1)
    n_chips = pg.evaluate("document.querySelectorAll('.cat-marquee .cat-pill').length")
    print("pills in band (incl. duplicate half):", n_chips)
    pg.locator(".cat-marquee").screenshot(path="shots/qa-marquee.png")

    # newsletter section
    pg.locator(".newsletter").scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    print("form action:", pg.get_attribute(".nl-form", "action"))
    pg.locator(".newsletter").screenshot(path="shots/qa-newsletter.png")

    # guides section (thumbnails on homepage)
    cards = pg.evaluate("""(() => {
        const sec = [...document.querySelectorAll('h2')].find(h => h.textContent.includes('Procreate Guides'));
        const grid = sec.closest('section').querySelectorAll('.art-card');
        return {cards: grid.length, imgs: sec.closest('section').querySelectorAll('.art-card .art-img').length};
    })()""")
    print("homepage guide cards:", cards)
    pg.locator(".arts-grid").last.scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    pg.screenshot(path="shots/qa-home-guides.png")

    # ── blog index: every card must have a thumbnail ──
    pg.goto(BASE + "/blog.html", wait_until="networkidle")
    n_cards = pg.evaluate("document.querySelectorAll('.art-card').length")
    n_imgs = pg.evaluate("document.querySelectorAll('.art-card .art-img').length")
    print(f"blog index: {n_cards} cards / {n_imgs} thumbnails")
    pg.screenshot(path="shots/qa-blog.png", full_page=False)

    # ── overflow check mobile on changed pages ──
    mp = b.new_context(viewport={"width": 390, "height": 844}).new_page()
    for url in ["/", "/blog.html"]:
        mp.goto(BASE + url, wait_until="load")
        mp.wait_for_timeout(600)
        ov = mp.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        print(f"overflow {url} @390px:", ov, "px")
    b.close()
print("QA DONE")
